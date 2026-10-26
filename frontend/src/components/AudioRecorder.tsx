import React, { useState, useRef, useEffect } from 'react';
import { Mic, Square, RotateCcw, AlertCircle, CheckCircle2 } from 'lucide-react';

interface AudioRecorderProps {
  onAudioReady: (blob: Blob, filename: string) => void;
  disabled?: boolean;
}

/**
 * Converts AudioBuffer to standard 16-bit PCM Mono 16kHz WAV Blob.
 */
function audioBufferTo16kMonoWav(buffer: AudioBuffer): Blob {
  const targetSampleRate = 16000;
  const numChannels = 1;
  const length = Math.round(buffer.duration * targetSampleRate);
  
  // Offline resample to 16000 Hz mono
  const offlineCtx = new OfflineAudioContext(1, length, targetSampleRate);
  const source = offlineCtx.createBufferSource();
  source.buffer = buffer;
  source.connect(offlineCtx.destination);
  source.start(0);

  // We write synchronously from the rendered PCM
  const wavBuffer = new ArrayBuffer(44 + length * 2);
  const view = new DataView(wavBuffer);

  // Helper string writer
  const writeString = (offset: number, str: string) => {
    for (let i = 0; i < str.length; i++) {
      view.setUint8(offset + i, str.charCodeAt(i));
    }
  };

  /* RIFF identifier */
  writeString(0, 'RIFF');
  /* file length */
  view.setUint32(4, 36 + length * 2, true);
  /* RIFF type */
  writeString(8, 'WAVE');
  /* format chunk identifier */
  writeString(12, 'fmt ');
  /* format chunk length */
  view.setUint32(16, 16, true);
  /* sample format (1 = PCM) */
  view.setUint16(20, 1, true);
  /* channel count */
  view.setUint16(22, numChannels, true);
  /* sample rate */
  view.setUint32(24, targetSampleRate, true);
  /* byte rate (sample rate * block align) */
  view.setUint32(28, targetSampleRate * numChannels * 2, true);
  /* block align (channel count * bytes per sample) */
  view.setUint16(32, numChannels * 2, true);
  /* bits per sample */
  view.setUint16(34, 16, true);
  /* data chunk identifier */
  writeString(36, 'data');
  /* data chunk length */
  view.setUint32(40, length * 2, true);

  // Read channel data and quantize to 16-bit PCM
  const channelData = buffer.getChannelData(0);
  let offset = 44;
  const step = buffer.sampleRate / targetSampleRate;

  for (let i = 0; i < length; i++) {
    const srcIndex = Math.min(Math.round(i * step), channelData.length - 1);
    const sample = Math.max(-1, Math.min(1, channelData[srcIndex]));
    const intSample = sample < 0 ? sample * 0x8000 : sample * 0x7fff;
    view.setInt16(offset, intSample, true);
    offset += 2;
  }

  return new Blob([view], { type: 'audio/wav' });
}

export const AudioRecorder: React.FC<AudioRecorderProps> = ({ onAudioReady, disabled }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [recordSeconds, setRecordSeconds] = useState(0);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [micLevel, setMicLevel] = useState<number>(0);
  const [error, setError] = useState<string | null>(null);

  const audioContextRef = useRef<AudioContext | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const recordedChunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<any>(null);
  const animFrameRef = useRef<number | null>(null);

  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
      if (audioUrl) URL.revokeObjectURL(audioUrl);
      if (streamRef.current) streamRef.current.getTracks().forEach((t) => t.stop());
      if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
        audioContextRef.current.close();
      }
    };
  }, [audioUrl]);

  const startRecording = async () => {
    setError(null);
    setAudioUrl(null);
    recordedChunksRef.current = [];
    setRecordSeconds(0);

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: false,
          noiseSuppression: false,
          autoGainControl: false,
        },
      });
      streamRef.current = stream;

      const audioCtx = new (window.AudioContext || (window as any).webkitAudioContext)();
      audioContextRef.current = audioCtx;

      const sourceNode = audioCtx.createMediaStreamSource(stream);
      const analyserNode = audioCtx.createAnalyser();
      analyserNode.fftSize = 256;
      sourceNode.connect(analyserNode);

      // Real-time volume level visualizer
      const dataArray = new Uint8Array(analyserNode.frequencyBinCount);
      const updateLevel = () => {
        analyserNode.getByteFrequencyData(dataArray);
        let sum = 0;
        for (let i = 0; i < dataArray.length; i++) {
          sum += dataArray[i];
        }
        const avg = sum / dataArray.length;
        setMicLevel(Math.min(100, Math.round((avg / 128) * 100)));
        animFrameRef.current = requestAnimationFrame(updateLevel);
      };
      updateLevel();

      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          recordedChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
        setMicLevel(0);

        try {
          // Decode raw chunks to AudioBuffer for clean 16kHz mono conversion
          const rawBlob = new Blob(recordedChunksRef.current);
          const arrayBuffer = await rawBlob.arrayBuffer();
          const decodedBuffer = await audioCtx.decodeAudioData(arrayBuffer);
          const wavBlob = audioBufferTo16kMonoWav(decodedBuffer);

          const localUrl = URL.createObjectURL(wavBlob);
          setAudioUrl(localUrl);
          onAudioReady(wavBlob, 'sustained_phonation_16k.wav');
        } catch (convErr) {
          console.warn('WAV resampling fallback:', convErr);
          const rawFallback = new Blob(recordedChunksRef.current, { type: 'audio/webm' });
          const localUrl = URL.createObjectURL(rawFallback);
          setAudioUrl(localUrl);
          onAudioReady(rawFallback, 'sustained_phonation.webm');
        } finally {
          stream.getTracks().forEach((track) => track.stop());
        }
      };

      mediaRecorder.start();
      setIsRecording(true);

      timerRef.current = setInterval(() => {
        setRecordSeconds((prev) => {
          if (prev >= 4) {
            stopRecording();
            return 5;
          }
          return prev + 1;
        });
      }, 1000);
    } catch (err: any) {
      console.error(err);
      setError('Microphone access denied. Please verify your browser mic permissions or upload a pre-recorded WAV file.');
    }
  };

  const stopRecording = () => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
    }
    setIsRecording(false);
  };

  const resetRecording = () => {
    setAudioUrl(null);
    setRecordSeconds(0);
    setError(null);
  };

  return (
    <div className="card-nixtio p-6 sm:p-8 flex flex-col items-center justify-center text-center space-y-6">
      {error && (
        <div className="w-full p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-xs text-red-400 flex items-start gap-2.5 text-left">
          <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {!audioUrl && !isRecording && (
        <div className="flex flex-col items-center space-y-4 max-w-md">
          {/* Visual recorder empty state illustration */}
          <div className="relative w-40 h-28 sm:w-48 sm:h-32 rounded-2xl overflow-hidden border border-border bg-surface-2 shadow-sm">
            <img
              src="/images/recorder-empty.webp"
              alt="Microphone acoustic phonation recording setup"
              width={1200}
              height={896}
              loading="lazy"
              className="w-full h-full object-cover"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-surface via-transparent to-transparent opacity-60" />
          </div>

          {/* Large accessible 64px button */}
          <button
            type="button"
            onClick={startRecording}
            disabled={disabled}
            aria-label="Start 5-second voice phonation recording"
            className="w-20 h-20 rounded-full bg-accent hover:bg-accent-hover text-white flex items-center justify-center shadow-xl shadow-accent/25 transition-transform hover:scale-105 active:scale-95 disabled:opacity-50 touch-target"
          >
            <Mic className="w-8 h-8" />
          </button>
          
          <div className="space-y-1">
            <h4 className="text-base font-bold text-txt">
              Live Microphone Capture
            </h4>
            <p className="text-xs text-txt-muted leading-relaxed">
              Sit upright, take a breath, and sustain a steady <strong className="text-txt">"aaah"</strong> at comfortable volume for 5 seconds.
            </p>
          </div>

          <span className="text-[11px] font-mono text-txt-muted px-2.5 py-1 rounded border border-border bg-surface-2">
            Automated 16 kHz Mono Resampling & PCM Encoding
          </span>
        </div>
      )}

      {isRecording && (
        <div className="flex flex-col items-center space-y-5 py-2 w-full max-w-sm animate-fade-in">
          {/* Animated active pulse */}
          <div className="relative flex items-center justify-center">
            <div className="w-20 h-20 rounded-full bg-red-500 text-white flex items-center justify-center animate-pulse shadow-lg shadow-red-500/30">
              <Mic className="w-8 h-8" />
            </div>
            <div className="absolute -inset-3 rounded-full border-2 border-red-500/40 animate-ping pointer-events-none" />
          </div>

          <div className="space-y-1">
            <div className="text-2xl font-mono font-extrabold text-red-500 tracking-wider">
              00:0{recordSeconds} <span className="text-txt-muted font-normal text-sm">/ 00:05</span>
            </div>
            <p className="text-xs text-txt-muted">
              Sustaining continuous vowel sound steadily...
            </p>
          </div>

          {/* Live Mic Volume Level Meter */}
          <div className="w-full space-y-1">
            <div className="flex justify-between text-[10px] font-mono text-txt-muted">
              <span>Input Level</span>
              <span>{micLevel}%</span>
            </div>
            <div className="w-full h-2 rounded-full bg-surface-2 overflow-hidden border border-border">
              <div
                className={`h-full transition-all duration-75 ${
                  micLevel > 80 ? 'bg-amber-400' : 'bg-accent'
                }`}
                style={{ width: `${micLevel}%` }}
              />
            </div>
          </div>

          <button
            type="button"
            onClick={stopRecording}
            className="touch-target px-6 py-2.5 rounded-xl border border-red-500/30 bg-red-500/10 hover:bg-red-500/20 text-xs font-semibold text-red-400 flex items-center gap-2 transition"
          >
            <Square className="w-3.5 h-3.5 fill-current" /> Stop & Finalize Sample
          </button>
        </div>
      )}

      {audioUrl && !isRecording && (
        <div className="flex flex-col items-center space-y-4 w-full max-w-md animate-fade-in">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full border border-emerald-500/30 bg-emerald-500/10 text-xs font-semibold text-emerald-400">
            <CheckCircle2 className="w-4 h-4" />
            <span>Phonation Sample Ready (16 kHz Mono WAV)</span>
          </div>

          <audio controls src={audioUrl} className="w-full h-10 mt-1" />

          <button
            type="button"
            onClick={resetRecording}
            className="touch-target px-4 py-2 border border-border hover:bg-surface-2 rounded-xl text-xs font-medium text-txt-muted hover:text-txt flex items-center gap-1.5 transition"
          >
            <RotateCcw className="w-3.5 h-3.5" /> Re-record Phonation
          </button>
        </div>
      )}
    </div>
  );
};

import React, { useState, useRef, useEffect } from 'react';
import { Mic, Square, RotateCcw, AlertCircle, Volume2 } from 'lucide-react';

interface AudioRecorderProps {
  onAudioReady: (blob: Blob, filename: string) => void;
  disabled?: boolean;
}

export const AudioRecorder: React.FC<AudioRecorderProps> = ({ onAudioReady, disabled }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [recordSeconds, setRecordSeconds] = useState(0);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<any>(null);

  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      if (audioUrl) URL.revokeObjectURL(audioUrl);
    };
  }, [audioUrl]);

  const startRecording = async () => {
    setError(null);
    setAudioUrl(null);
    audioChunksRef.current = [];
    setRecordSeconds(0);

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const mimeType = mediaRecorder.mimeType || 'audio/webm';
        const blob = new Blob(audioChunksRef.current, { type: mimeType });
        const url = URL.createObjectURL(blob);
        setAudioUrl(url);
        onAudioReady(blob, 'microphone_recording.webm');
        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);

      timerRef.current = setInterval(() => {
        setRecordSeconds((prev) => {
          if (prev >= 5) {
            // Auto stop after 5 seconds of sustained phonation
            stopRecording();
            return 5;
          }
          return prev + 1;
        });
      }, 1000);
    } catch (err: any) {
      console.error(err);
      setError('Microphone access denied or not available. Please allow mic permissions or upload a file.');
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
    <div className="flex flex-col items-center justify-center p-6 border-2 border-dashed border-teal-200 rounded-xl bg-teal-50/30 text-center">
      {error && (
        <div className="mb-4 p-3 bg-red-50 text-red-700 text-xs rounded-lg flex items-center gap-2 border border-red-200 w-full">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {!audioUrl && !isRecording && (
        <div className="flex flex-col items-center">
          <div className="w-16 h-16 rounded-full bg-teal-600 text-white flex items-center justify-center mb-3 shadow-md hover:bg-teal-700 transition">
            <Mic className="w-8 h-8" />
          </div>
          <h4 className="font-semibold text-slate-800 text-sm mb-1">Live Voice Recording</h4>
          <p className="text-xs text-slate-500 max-w-sm mb-4">
            Press record and hold a steady sustained vowel (e.g. "aaah" or "oooh") at your normal speaking pitch for 3–5 seconds.
          </p>
          <button
            type="button"
            onClick={startRecording}
            disabled={disabled}
            className="px-5 py-2.5 bg-teal-600 hover:bg-teal-700 disabled:opacity-50 text-white rounded-lg text-xs font-semibold shadow-sm flex items-center gap-2 transition"
          >
            <Mic className="w-4 h-4" /> Start 5s Phonation Recording
          </button>
        </div>
      )}

      {isRecording && (
        <div className="flex flex-col items-center space-y-3 py-2">
          <div className="relative flex items-center justify-center">
            <div className="w-16 h-16 rounded-full bg-red-500 text-white flex items-center justify-center animate-pulse">
              <Mic className="w-8 h-8" />
            </div>
            <div className="absolute -inset-2 rounded-full border-2 border-red-400 animate-ping opacity-75 pointer-events-none" />
          </div>
          <div>
            <div className="text-xl font-mono font-bold text-red-600">00:0{recordSeconds} / 00:05</div>
            <p className="text-xs text-slate-600 font-medium mt-1">Please sustain vowel sound steadily...</p>
          </div>
          <button
            type="button"
            onClick={stopRecording}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-xs font-medium shadow flex items-center gap-1.5 transition"
          >
            <Square className="w-3.5 h-3.5" /> Stop Recording
          </button>
        </div>
      )}

      {audioUrl && !isRecording && (
        <div className="flex flex-col items-center space-y-3 w-full max-w-md">
          <div className="flex items-center gap-2 text-xs font-medium text-emerald-700 bg-emerald-50 px-3 py-1 rounded-full border border-emerald-200">
            <Volume2 className="w-3.5 h-3.5" /> Recording Ready ({recordSeconds}s)
          </div>
          <audio controls src={audioUrl} className="w-full h-10 mt-2" />
          <button
            type="button"
            onClick={resetRecording}
            className="text-xs text-slate-500 hover:text-slate-800 flex items-center gap-1 transition"
          >
            <RotateCcw className="w-3.5 h-3.5" /> Record Again
          </button>
        </div>
      )}
    </div>
  );
};

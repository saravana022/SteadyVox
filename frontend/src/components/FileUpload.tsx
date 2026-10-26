import React, { useState, useRef } from 'react';
import { UploadCloud, FileAudio, X, AlertCircle } from 'lucide-react';

interface FileUploadProps {
  onFileSelected: (file: File) => void;
  disabled?: boolean;
}

export const FileUpload: React.FC<FileUploadProps> = ({ onFileSelected, disabled }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = (file: File) => {
    setError(null);
    const validExtensions = ['.wav', '.mp3', '.flac', '.ogg', '.webm', '.m4a', '.mp4'];
    const hasValidExt = validExtensions.some((ext) => file.name.toLowerCase().endsWith(ext));

    if (!hasValidExt && !file.type.startsWith('audio/')) {
      setError('Please provide a valid audio file (WAV, MP3, FLAC, or WebM).');
      return;
    }

    if (file.size > 20 * 1024 * 1024) {
      setError('Audio file size exceeds the 20MB limit.');
      return;
    }

    setSelectedFile(file);
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
    onFileSelected(file);
  };

  const clearFile = () => {
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setSelectedFile(null);
    setPreviewUrl(null);
    setError(null);
    if (inputRef.current) inputRef.current.value = '';
  };

  return (
    <div className="w-full space-y-4">
      {error && (
        <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-xs text-red-400 flex items-start gap-2.5">
          <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {!selectedFile ? (
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragOver(false);
            if (e.dataTransfer.files && e.dataTransfer.files[0]) {
              handleFile(e.dataTransfer.files[0]);
            }
          }}
          onClick={() => inputRef.current?.click()}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              inputRef.current?.click();
            }
          }}
          aria-label="Upload audio file"
          className={`card-nixtio p-10 flex flex-col items-center justify-center cursor-pointer transition text-center space-y-4 ${
            dragOver ? 'border-accent bg-accent-subtle' : 'hover:border-border-hover'
          }`}
        >
          <input
            ref={inputRef}
            type="file"
            accept="audio/*,.wav,.mp3,.flac,.webm,.m4a"
            disabled={disabled}
            onChange={(e) => {
              if (e.target.files && e.target.files[0]) {
                handleFile(e.target.files[0]);
              }
            }}
            className="hidden"
          />
          <div className="w-14 h-14 rounded-2xl bg-surface-2 border border-border text-accent flex items-center justify-center shadow-inner">
            <UploadCloud className="w-7 h-7" />
          </div>
          <div className="space-y-1">
            <p className="text-sm font-bold text-txt">Click to browse or drop an audio recording</p>
            <p className="text-xs text-txt-muted">Supports WAV, MP3, FLAC, WebM (Recommended: sustained vowel /a/)</p>
          </div>
        </div>
      ) : (
        <div className="card-nixtio p-5 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-accent-subtle text-accent border border-accent/20 flex items-center justify-center">
                <FileAudio className="w-5 h-5" />
              </div>
              <div className="text-left">
                <p className="text-xs font-bold text-txt truncate max-w-xs">{selectedFile.name}</p>
                <p className="text-[11px] font-mono text-txt-muted">{(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
              </div>
            </div>
            <button
              onClick={clearFile}
              className="touch-target p-2 text-txt-muted hover:text-red-400 rounded-lg transition"
              title="Remove file"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
          {previewUrl && <audio controls src={previewUrl} className="w-full h-10 mt-2" />}
        </div>
      )}
    </div>
  );
};

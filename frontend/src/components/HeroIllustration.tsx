import React from 'react';

export const HeroIllustration: React.FC<{ className?: string }> = ({ className = '' }) => {
  return (
    <div className={`relative flex items-center justify-center ${className}`}>
      <svg
        viewBox="0 0 600 340"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="w-full h-auto max-w-lg drop-shadow-2xl"
        role="img"
        aria-label="Acoustic waveform analysis and neural pathway illustration"
      >
        <defs>
          <linearGradient id="waveGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="var(--accent)" stopOpacity="0.8" />
            <stop offset="50%" stopColor="#38bdf8" stopOpacity="0.9" />
            <stop offset="100%" stopColor="#818cf8" stopOpacity="0.8" />
          </linearGradient>
          <linearGradient id="glowGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="var(--accent)" stopOpacity="0.25" />
            <stop offset="100%" stopColor="var(--accent)" stopOpacity="0" />
          </linearGradient>
          <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="6" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
        </defs>

        {/* Outer Tech Frame */}
        <rect
          x="20"
          y="20"
          width="560"
          height="300"
          rx="24"
          fill="var(--surface)"
          stroke="var(--border)"
          strokeWidth="1.5"
        />

        {/* Grid Background Lines */}
        <g opacity="0.15" stroke="var(--text-muted)" strokeWidth="0.8" strokeDasharray="4 4">
          <line x1="60" y1="80" x2="540" y2="80" />
          <line x1="60" y1="140" x2="540" y2="140" />
          <line x1="60" y1="200" x2="540" y2="200" />
          <line x1="60" y1="260" x2="540" y2="260" />
          <line x1="160" y1="40" x2="160" y2="300" />
          <line x1="300" y1="40" x2="300" y2="300" />
          <line x1="440" y1="40" x2="440" y2="300" />
        </g>

        {/* Shaded Area Under Wave */}
        <path
          d="M 60 170 
             Q 100 130, 140 170 
             T 220 170 
             Q 260 90, 300 170 
             T 380 170 
             Q 420 220, 460 170 
             T 540 170 
             L 540 270 
             L 60 270 Z"
          fill="url(#glowGrad)"
        />

        {/* Sustained Phonation Sine & Micro-Perturbation Waveform */}
        <path
          d="M 60 170 
             Q 100 130, 140 170 
             T 220 170 
             Q 260 80, 300 170 
             T 380 170 
             Q 420 230, 460 170 
             T 540 170"
          stroke="url(#waveGrad)"
          strokeWidth="3"
          strokeLinecap="round"
          filter="url(#glow)"
        />

        {/* Second High Frequency Harmonic Wave */}
        <path
          d="M 60 170 
             Q 80 155, 100 170 
             T 140 170 
             Q 160 145, 180 170 
             T 220 170 
             Q 240 150, 260 170 
             T 300 170 
             Q 320 140, 340 170 
             T 380 170 
             Q 400 155, 420 170 
             T 460 170 
             Q 480 150, 500 170 
             T 540 170"
          stroke="var(--accent)"
          strokeWidth="1.5"
          opacity="0.4"
          strokeDasharray="2 3"
        />

        {/* Feature Extraction Node Points */}
        <g>
          <circle cx="140" cy="170" r="4.5" fill="var(--bg)" stroke="var(--accent)" strokeWidth="2.5" />
          <circle cx="260" cy="80" r="5" fill="#38bdf8" stroke="var(--bg)" strokeWidth="2" />
          <circle cx="300" cy="170" r="4.5" fill="var(--bg)" stroke="#818cf8" strokeWidth="2.5" />
          <circle cx="420" cy="230" r="5" fill="var(--accent)" stroke="var(--bg)" strokeWidth="2" />
          <circle cx="460" cy="170" r="4.5" fill="var(--bg)" stroke="var(--accent)" strokeWidth="2.5" />
        </g>

        {/* Feature Extraction Tags */}
        <g font-family="monospace" font-size="10" fill="var(--text-muted)">
          <rect x="70" y="45" width="85" height="22" rx="6" fill="var(--surface-2)" stroke="var(--border)" />
          <text x="80" y="60" fill="var(--text)" font-weight="bold">F0: 224 Hz</text>

          <rect x="235" y="45" width="90" height="22" rx="6" fill="var(--surface-2)" stroke="var(--border)" />
          <text x="245" y="60" fill="#38bdf8" font-weight="bold">Jitter: 0.38%</text>

          <rect x="430" y="45" width="95" height="22" rx="6" fill="var(--surface-2)" stroke="var(--border)" />
          <text x="440" y="60" fill="#818cf8" font-weight="bold">HNR: 24.2 dB</text>
        </g>

        {/* Calibrated Classifier Status Pill */}
        <g>
          <rect x="180" y="270" width="240" height="26" rx="13" fill="var(--surface-2)" stroke="var(--border)" />
          <circle cx="198" cy="283" r="4" fill="#10b981" />
          <text x="210" y="287" font-family="monospace" font-size="10" fill="var(--text)" font-weight="600">
            Praat MDVP • Calibrated Random Forest
          </text>
        </g>
      </svg>
    </div>
  );
};

import React, { useEffect, useRef } from 'react';

interface WaveformCanvasProps {
  className?: string;
}

export const WaveformCanvas: React.FC<WaveformCanvasProps> = ({ className = '' }) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;
    let isVisible = true;
    let time = 0;

    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // Responsive canvas resizing
    const resizeCanvas = () => {
      const rect = canvas.getBoundingClientRect();
      const dpr = window.devicePixelRatio || 1;
      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;
      ctx.scale(dpr, dpr);
    };

    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Pause animation when off-screen
    const observer = new IntersectionObserver(([entry]) => {
      isVisible = entry.isIntersecting;
    });
    observer.observe(canvas);

    // Render loop
    const render = () => {
      if (isVisible && !prefersReducedMotion) {
        const width = canvas.clientWidth;
        const height = canvas.clientHeight;

        ctx.clearRect(0, 0, width, height);

        // Draw multiple harmonic wave layers (simulating sustained phonation + tremor)
        const waves = [
          { freq: 0.012, amp: 28, speed: 0.03, tremorFreq: 0.005, color: 'rgba(99, 102, 241, 0.45)', lineWidth: 2 },
          { freq: 0.020, amp: 18, speed: 0.045, tremorFreq: 0.007, color: 'rgba(129, 140, 248, 0.30)', lineWidth: 1.5 },
          { freq: 0.008, amp: 38, speed: 0.02, tremorFreq: 0.004, color: 'rgba(165, 180, 252, 0.20)', lineWidth: 1 },
        ];

        const centerY = height / 2;

        waves.forEach((w) => {
          ctx.beginPath();
          ctx.strokeStyle = w.color;
          ctx.lineWidth = w.lineWidth;

          for (let x = 0; x < width; x += 3) {
            // Harmonic carrier + micro-tremor modulation (4–7 Hz analog)
            const tremorMod = 1 + 0.25 * Math.sin(x * w.tremorFreq + time * 1.5);
            const y = centerY + Math.sin(x * w.freq + time * w.speed) * w.amp * tremorMod;
            if (x === 0) {
              ctx.moveTo(x, y);
            } else {
              ctx.lineTo(x, y);
            }
          }
          ctx.stroke();
        });

        time += 0.5;
      }

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener('resize', resizeCanvas);
      observer.disconnect();
    };
  }, []);

  return (
    <div className={`relative overflow-hidden ${className}`}>
      <canvas
        ref={canvasRef}
        aria-hidden="true"
        className="w-full h-full block"
      />
      {/* Subtle edge fade gradient */}
      <div className="absolute inset-0 pointer-events-none bg-gradient-to-r from-bg via-transparent to-bg" />
      <div className="absolute inset-0 pointer-events-none bg-gradient-to-b from-transparent via-transparent to-bg" />
    </div>
  );
};

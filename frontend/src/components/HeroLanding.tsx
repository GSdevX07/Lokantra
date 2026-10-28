// React is supplied by the frontend runtime; keep the import in one place for the hook APIs.
// @ts-ignore The editor may not have the frontend dependencies resolved yet.
import React, { useState, useEffect, useRef, useCallback } from 'react';

export interface HeroLandingProps {
  brandName?: string;
  tagline?: string;
  typewriterText?: string;
  email?: string;
  onNavigate?: (section: string) => void;
}

/**
 * Custom hook for typewriter text effect
 * @param text The full text to type out
 * @param speed Typing interval in milliseconds (default: 38ms)
 * @param startDelay Delay before typing begins (default: 600ms)
 */
export function useTypewriter(text: string, speed = 38, startDelay = 600) {
  const [displayed, setDisplayed] = useState('');
  const [done, setDone] = useState(false);

  useEffect(() => {
    setDisplayed('');
    setDone(false);

    let currentIndex = 0;
    let timer: ReturnType<typeof setTimeout> | null = null;
    let interval: ReturnType<typeof setInterval> | null = null;

    timer = setTimeout(() => {
      interval = setInterval(() => {
        if (currentIndex < text.length) {
          setDisplayed(text.slice(0, currentIndex + 1));
          currentIndex++;
        } else {
          setDone(true);
          if (interval) clearInterval(interval);
        }
      }, speed);
    }, startDelay);

    return () => {
      if (timer) clearTimeout(timer);
      if (interval) clearInterval(interval);
    };
  }, [text, speed, startDelay]);

  return { displayed, done };
}

export const HeroLanding: React.FC<HeroLandingProps> = ({
  brandName = 'LOK\u0100NTRA',
  tagline = 'Concise & Universal Swarm Intelligence Engine',
  typewriterText = 'LOK\u0100NTRA extracts reality. Auto-Generate Parallel World. Million-Scale Agents. God\'s-Eye View. Optimal Solution in Complex Dynamics.',
  email = 'contact@lokantra.ai',
  onNavigate
}) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [pillsVisible, setPillsVisible] = useState(false);

  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const targetFrameRef = useRef<number>(48);
  const currentFrameRef = useRef<number>(48);
  const imagesRef = useRef<HTMLImageElement[]>([]);
  const animIdRef = useRef<number | null>(null);

  const { displayed, done } = useTypewriter(typewriterText, 38, 600);

  // Trigger pill buttons animation 400ms after mount
  useEffect(() => {
    const timer = setTimeout(() => {
      setPillsVisible(true);
    }, 400);
    return () => clearTimeout(timer);
  }, []);

  // Preload frames and start canvas render loop
  useEffect(() => {
    const TOTAL_FRAMES = 97;
    const canvas = canvasRef.current;
    const images: HTMLImageElement[] = [];

    const drawFrame = (frameIndex: number) => {
      if (!canvas) return;
      const ctx = canvas.getContext('2d', { alpha: false });
      if (!ctx) return;
      const idx = Math.max(0, Math.min(TOTAL_FRAMES - 1, Math.round(frameIndex)));
      const img = images[idx];
      if (img && img.complete && img.naturalWidth > 0) {
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
      }
    };

    let hasDrawn = false;
    for (let i = 0; i < TOTAL_FRAMES; i++) {
      const img = new Image();
      img.src = `/frames/f_${String(i).padStart(3, '0')}.webp`;
      img.onload = () => {
        if (!hasDrawn || i === 48) {
          drawFrame(48);
          hasDrawn = true;
        }
      };
      images.push(img);
    }
    imagesRef.current = images;

    // Render loop
    const render = () => {
      const diff = targetFrameRef.current - currentFrameRef.current;
      if (Math.abs(diff) > 0.02) {
        const factor = Math.abs(diff) > 15 ? 0.45 : 0.28;
        currentFrameRef.current += diff * factor;
        drawFrame(currentFrameRef.current);
      }
      animIdRef.current = requestAnimationFrame(render);
    };
    animIdRef.current = requestAnimationFrame(render);

    const handleMouseMove = (e: MouseEvent) => {
      const ratio = Math.max(0, Math.min(1, e.clientX / window.innerWidth));
      targetFrameRef.current = ratio * (TOTAL_FRAMES - 1);
    };

    const handleTouchMove = (e: TouchEvent) => {
      if (e.touches && e.touches.length > 0) {
        const ratio = Math.max(0, Math.min(1, e.touches[0].clientX / window.innerWidth));
        targetFrameRef.current = ratio * (TOTAL_FRAMES - 1);
      }
    };

    window.addEventListener('mousemove', handleMouseMove, { passive: true });
    window.addEventListener('touchmove', handleTouchMove, { passive: true });

    return () => {
      if (animIdRef.current) cancelAnimationFrame(animIdRef.current);
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('touchmove', handleTouchMove);
    };
  }, []);


  const handleNav = (target: string) => {
    setMobileMenuOpen(false);
    if (onNavigate) {
      onNavigate(target);
    } else {
      const el = document.getElementById(target);
      if (el) {
        el.scrollIntoView({ behavior: 'smooth' });
      }
    }
  };

  return (
    <div className="relative min-h-screen w-full overflow-x-hidden text-black select-none font-(--font-body)">
      {/* Interactive Background Canvas (0-latency preloaded frame sequence) */}
      <canvas
        ref={canvasRef}
        width={1920}
        height={1085}
        className="fixed inset-0 w-full h-full object-cover z-0 pointer-events-none transition-transform duration-500 ease-out"
        style={{
          objectPosition: 'left center',
          transform: 'scale(1.1)',
          transformOrigin: 'left center'
        }}
      />

      {/* Subtle vignette gradient on the left to ensure text pops with high legibility */}
      <div className="fixed inset-0 pointer-events-none z-0 bg-linear-to-r from-white/30 via-white/10 to-transparent" />

      {/* Centered Fixed Wordmark Logo (does not scroll) */}
      <header className="fixed top-3 sm:top-3 md:top-6 left-1/2 -translate-x-1/2 z-20 pointer-events-auto flex justify-center items-center">
        <img
          src="/src/assets/logo/lokantra_wordmark.png"
          alt="LOK\u0100NTRA"
          className="h-12 sm:h-16 md:h-20 lg:h-24 max-w-[85vw] w-auto object-contain cursor-pointer select-none filter drop-shadow-[0_2px_12px_rgba(0,0,0,0.06)] hover:opacity-90 hover:scale-[1.02] transition-all duration-300"
          onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
          title="LOK\u0100NTRA - Back to top"
        />
      </header>

      {/* Hero Section (z-index: 1) */}
      <section className="min-h-screen w-full flex flex-col justify-center px-6 sm:px-12 md:px-16 lg:px-24 xl:px-28 pt-32 sm:pt-36 md:pt-40 pb-16 md:pb-20 relative z-1 overflow-hidden">
        <div className="w-full max-w-xl lg:max-w-2xl relative z-10 flex flex-col items-start text-left">
          {/* 1. Blurred intro label */}
          <div
            className="pointer-events-none select-none mb-3 sm:mb-4"
            style={{
              fontSize: 'clamp(16px, 2.1vw, 22px)',
              lineHeight: 1.35,
              fontWeight: 400,
              color: 'rgba(0, 0, 0, 0.7)',
              filter: 'blur(1.5px)',
              fontFamily: 'var(--font-body)'
            }}
          >
            Hey there, meet {brandName},<br />
            {tagline}
          </div>

          {/* 2. Bold Unique Crazy Hero Highlight */}
          <div className="hero-highlight-wrap mb-4 sm:mb-6 select-none">
            <h1 className="hero-highlight-title">
              <span className="hero-text-dark">Upload Reports,</span>
              <span className="hero-text-gold">Predict The Unseen</span>
            </h1>
          </div>

          {/* 3. Blurred normal content (Typewriter text) */}
          <p
            className="text-black mb-6 sm:mb-8 select-text pointer-events-none"
            style={{
              fontSize: 'clamp(17px, 2.3vw, 24px)',
              lineHeight: 1.45,
              fontWeight: 400,
              minHeight: '64px',
              fontFamily: 'var(--font-body)',
              letterSpacing: '-0.01em',
              filter: 'blur(1.5px)'
            }}
          >
            {displayed}
            {!done && (
              <span
                className="inline-block w-0.5 h-[1.15em] bg-black align-middle ml-0.5"
                style={{ animation: 'blink 1s step-end infinite' }}
              />
            )}
          </p>

          {/* 3. Action pill buttons */}
          <div
            className="flex flex-wrap items-center gap-4 sm:gap-3.5 transition-all duration-500 ease-out pt-2"
            style={{
              opacity: pillsVisible ? 1 : 0,
              transform: pillsVisible ? 'translateY(0)' : 'translateY(12px)'
            }}
          >
            <button
              onClick={() => handleNav('simulation-console')}
              className="inline-flex items-center justify-center bg-white/95 backdrop-blur-md text-black border border-black/15 hover:border-black hover:bg-black hover:text-white px-5 sm:px-6 py-2.5 sm:py-3 rounded-full text-[13px] sm:text-[14px] font-medium tracking-wide shadow-sm hover:shadow-md transition-all duration-200 cursor-pointer"
              style={{ fontFamily: 'var(--font-body)' }}
            >
              Start Simulation
            </button>

            <button
              onClick={() => handleNav('workflow-section')}
              className="inline-flex items-center justify-center bg-white/95 backdrop-blur-md text-black border border-black/15 hover:border-black hover:bg-black hover:text-white px-5 sm:px-6 py-2.5 sm:py-3 rounded-full text-[13px] sm:text-[14px] font-medium tracking-wide shadow-sm hover:shadow-md transition-all duration-200 cursor-pointer"
              style={{ fontFamily: 'var(--font-body)' }}
            >
              Explore Workflow
            </button>

            <button
              onClick={() => handleNav('history-section')}
              className="inline-flex items-center justify-center bg-white/95 backdrop-blur-md text-black border border-black/15 hover:border-black hover:bg-black hover:text-white px-5 sm:px-6 py-2.5 sm:py-3 rounded-full text-[13px] sm:text-[14px] font-medium tracking-wide shadow-sm hover:shadow-md transition-all duration-200 cursor-pointer"
              style={{ fontFamily: 'var(--font-body)' }}
            >
              History Database
            </button>

            <button
              onClick={() => handleNav('dashboard-section')}
              className="inline-flex items-center justify-center bg-white/95 backdrop-blur-md text-black border border-black/15 hover:border-black hover:bg-black hover:text-white px-5 sm:px-6 py-2.5 sm:py-3 rounded-full text-[13px] sm:text-[14px] font-medium tracking-wide shadow-sm hover:shadow-md transition-all duration-200 cursor-pointer"
              style={{ fontFamily: 'var(--font-body)' }}
            >
              System Architecture
            </button>


          </div>
        </div>

        {/* Scroll down indicator button with generous margin */}
        <button
          onClick={() => handleNav('simulation-console')}
          className="absolute bottom-8 right-8 sm:bottom-12 sm:right-14 md:bottom-14 md:right-20 w-12 h-12 rounded-full border border-black/20 bg-white/85 backdrop-blur-md text-black flex items-center justify-center text-lg hover:bg-black hover:text-white transition-all duration-300 cursor-pointer z-10 shadow-md hover:scale-105"
          title="Scroll down to simulation console"
        >
          {'\u2193'}
        </button>
      </section>
    </div>
  );
};

export default HeroLanding;

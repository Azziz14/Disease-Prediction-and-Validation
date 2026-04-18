import React, { useEffect, useRef } from 'react';

interface Particle {
  x: number;
  y: number;
  baseX: number;
  baseY: number;
  size: number;
  vx: number;
  vy: number;
  color: string; // 'green' | 'blue' | 'purple'
  alpha: number;
  pulseSpeed: number;
  pulsePhase: number;
}

const COLORS = {
  green: { r: 57, g: 255, b: 20 },
  blue: { r: 0, g: 243, b: 255 },
  purple: { r: 176, g: 91, b: 255 },
};

const CyberParticleBackground: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    // ——— Create particles ———
    const particles: Particle[] = [];
    // Capped at 120 to prevent O(N^2) line-drawing algorithm from dropping frames
    const PARTICLE_COUNT = Math.min(Math.floor((width * height) / 8000), 120);
    const colorKeys = Object.keys(COLORS) as Array<keyof typeof COLORS>;

    for (let i = 0; i < PARTICLE_COUNT; i++) {
      const x = Math.random() * width;
      const y = Math.random() * height;
      const colorKey = colorKeys[Math.floor(Math.random() * colorKeys.length)];
      particles.push({
        x,
        y,
        baseX: x,
        baseY: y,
        size: Math.random() * 2.5 + 1,
        vx: (Math.random() - 0.5) * 0.3,
        vy: (Math.random() - 0.5) * 0.3,
        color: colorKey,
        alpha: Math.random() * 0.5 + 0.3,
        pulseSpeed: Math.random() * 0.02 + 0.005,
        pulsePhase: Math.random() * Math.PI * 2,
      });
    }

    let mouseX = -9999;
    let mouseY = -9999;
    let frameCount = 0;

    const handleMouseMove = (e: MouseEvent) => {
      mouseX = e.clientX;
      mouseY = e.clientY;
    };

    const handleResize = () => {
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    };

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('resize', handleResize);

    let animationFrameId: number;

    const render = () => {
      frameCount++;
      ctx.clearRect(0, 0, width, height);

      // ══════════════ GRID ══════════════
      const gridSize = 50;
      ctx.lineWidth = 0.5;

      // Vertical lines
      for (let x = 0; x < width; x += gridSize) {
        const distToMouse = Math.abs(x - mouseX);
        const glow = distToMouse < 200 ? 0.12 - (distToMouse / 200) * 0.08 : 0.04;
        ctx.strokeStyle = `rgba(0, 243, 255, ${glow})`;
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, height);
        ctx.stroke();
      }
      // Horizontal lines
      for (let y = 0; y < height; y += gridSize) {
        const distToMouse = Math.abs(y - mouseY);
        const glow = distToMouse < 200 ? 0.12 - (distToMouse / 200) * 0.08 : 0.04;
        ctx.strokeStyle = `rgba(0, 243, 255, ${glow})`;
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
      }

      // ══════════════ CONNECTION LINES ══════════════
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x;
          const dy = particles[i].y - particles[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 120) {
            const lineAlpha = (1 - dist / 120) * 0.15;
            ctx.strokeStyle = `rgba(0, 243, 255, ${lineAlpha})`;
            ctx.lineWidth = 0.5;
            ctx.beginPath();
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.stroke();
          }
        }
      }

      // ══════════════ PARTICLES ══════════════
      for (let i = 0; i < particles.length; i++) {
        const p = particles[i];

        // Gentle roaming
        p.x += p.vx;
        p.y += p.vy;

        // Wrap around screen edges
        if (p.x < -20) p.x = width + 20;
        if (p.x > width + 20) p.x = -20;
        if (p.y < -20) p.y = height + 20;
        if (p.y > height + 20) p.y = -20;

        // Cursor gravity effect
        const dx = mouseX - p.x;
        const dy = mouseY - p.y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < 250) {
          const force = (250 - dist) / 250;
          p.x += dx * force * 0.025;
          p.y += dy * force * 0.025;
        } else {
          // Slowly return to base position
          p.x += (p.baseX - p.x) * 0.005;
          p.y += (p.baseY - p.y) * 0.005;
        }

        // Pulsing alpha
        const pulse = Math.sin(frameCount * p.pulseSpeed + p.pulsePhase) * 0.3 + 0.7;
        const currentAlpha = p.alpha * pulse;

        // Brighten near cursor
        const cursorBoost = dist < 200 ? (1 - dist / 200) * 0.6 : 0;
        const finalAlpha = Math.min(currentAlpha + cursorBoost, 1);

        const c = COLORS[p.color as keyof typeof COLORS];

        // Glow effect (larger, dim circle behind)
        if (p.size > 1.5 || dist < 150) {
          const glowRadius = p.size * 4;
          const gradient = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, glowRadius);
          gradient.addColorStop(0, `rgba(${c.r}, ${c.g}, ${c.b}, ${finalAlpha * 0.3})`);
          gradient.addColorStop(1, `rgba(${c.r}, ${c.g}, ${c.b}, 0)`);
          ctx.fillStyle = gradient;
          ctx.beginPath();
          ctx.arc(p.x, p.y, glowRadius, 0, Math.PI * 2);
          ctx.fill();
        }

        // Core dot
        ctx.fillStyle = `rgba(${c.r}, ${c.g}, ${c.b}, ${finalAlpha})`;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fill();
      }

      // ══════════════ CURSOR RING ══════════════
      if (mouseX > 0 && mouseY > 0) {
        const ringPulse = Math.sin(frameCount * 0.03) * 0.15 + 0.25;
        ctx.strokeStyle = `rgba(0, 243, 255, ${ringPulse})`;
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.arc(mouseX, mouseY, 80 + Math.sin(frameCount * 0.02) * 10, 0, Math.PI * 2);
        ctx.stroke();

        // Inner ring
        ctx.strokeStyle = `rgba(176, 91, 255, ${ringPulse * 0.6})`;
        ctx.beginPath();
        ctx.arc(mouseX, mouseY, 40 + Math.sin(frameCount * 0.04) * 5, 0, Math.PI * 2);
        ctx.stroke();
      }

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('resize', handleResize);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none"
      style={{
        zIndex: 0,
        background: 'radial-gradient(ellipse at 50% 0%, #0d0e18 0%, #050508 60%, #020203 100%)',
      }}
    />
  );
};

export default CyberParticleBackground;

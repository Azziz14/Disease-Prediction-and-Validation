import React from 'react';
import { motion } from 'framer-motion';

interface ParticleBackgroundProps {
  particleCount?: number;
}

const ParticleBackground: React.FC<ParticleBackgroundProps> = ({ particleCount = 40 }) => {
  const particles = Array.from({ length: particleCount });

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none z-0">
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1.5 }}
        className="w-full h-full relative"
      >
        {particles.map((_, i) => {
          // Generate deterministic looking but random starting points for initial render stability
          const size = Math.random() * 4 + 1;
          const left = `${Math.random() * 100}%`;
          const top = `${Math.random() * 100}%`;
          const duration = Math.random() * 20 + 10;
          const delay = Math.random() * 5;

          return (
            <motion.div
              key={i}
              className="absolute rounded-full bg-blue-500/20"
              style={{
                width: size,
                height: size,
                left,
                top,
              }}
              animate={{
                y: [0, -40, 0],
                x: [0, (Math.random() - 0.5) * 40, 0],
                opacity: [0.1, 0.4, 0.1],
              }}
              transition={{
                duration,
                delay,
                repeat: Infinity,
                ease: "linear"
              }}
            />
          );
        })}
      </motion.div>
      
      {/* Soft gradient orb in background */}
      <div className="absolute top-1/4 left-1/4 w-[40rem] h-[40rem] bg-blue-400/5 rounded-full blur-[100px]" />
      <div className="absolute bottom-1/4 right-1/4 w-[35rem] h-[35rem] bg-indigo-400/5 rounded-full blur-[100px]" />
    </div>
  );
};

export default ParticleBackground;

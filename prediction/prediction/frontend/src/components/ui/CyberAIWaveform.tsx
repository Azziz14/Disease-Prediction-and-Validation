import React from 'react';
import { motion } from 'framer-motion';

const CyberAIWaveform: React.FC<{ isThinking?: boolean }> = ({ isThinking = true }) => {
  const bars = Array.from({ length: 5 });

  return (
    <div className="flex items-center justify-center gap-1.5 h-12">
      {bars.map((_, i) => (
        <motion.div
          key={i}
          className="w-1.5 rounded-full bg-[var(--neon-blue)] opacity-80"
          animate={{
            height: isThinking ? ["20%", "100%", "20%"] : "20%",
          }}
          transition={{
            duration: 1,
            repeat: isThinking ? Infinity : 0,
            ease: "easeInOut",
            delay: i * 0.15,
          }}
          style={{
            boxShadow: `0 0 10px var(--neon-blue)`,
          }}
        />
      ))}
    </div>
  );
};

export default CyberAIWaveform;

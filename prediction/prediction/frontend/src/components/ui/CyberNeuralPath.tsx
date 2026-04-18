import React from 'react';
import { motion } from 'framer-motion';

interface CyberNeuralPathProps {
  totalSteps: number;
  currentStep: number;
}

const CyberNeuralPath: React.FC<CyberNeuralPathProps> = ({ totalSteps, currentStep }) => {
  const progress = (currentStep / totalSteps) * 100;

  return (
    <div className="relative w-full max-w-2xl mx-auto mt-8 flex items-center justify-center">
      {/* Background Dim Line */}
      <div className="absolute top-1/2 left-0 w-full h-[2px] bg-white/10 -translate-y-1/2 rounded-full overflow-hidden">
        {/* Glowing Progress Line */}
        <motion.div 
          className="h-full bg-gradient-to-r from-[var(--neon-purple)] via-[var(--neon-blue)] to-[var(--neon-green)] shadow-[0_0_15px_var(--neon-blue)]"
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.8, ease: "easeInOut" }}
        />
      </div>

      {/* Nodes */}
      <div className="relative flex justify-between w-full">
        {Array.from({ length: totalSteps }).map((_, idx) => {
          const isCompleted = idx < currentStep;
          const isActive = idx === currentStep;
          
          return (
            <div key={idx} className="relative z-10 flex flex-col items-center">
              <motion.div 
                className={`w-4 h-4 rounded-full border-2 border-[var(--cyber-dark)] transition-all duration-500`}
                animate={{
                  backgroundColor: isCompleted ? "var(--neon-green)" : isActive ? "var(--neon-blue)" : "rgba(255,255,255,0.2)",
                  scale: isActive ? 1.4 : 1,
                  boxShadow: isCompleted 
                    ? "0 0 10px var(--neon-green)" 
                    : isActive 
                      ? "0 0 15px var(--neon-blue)" 
                      : "none"
                }}
              />
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default CyberNeuralPath;

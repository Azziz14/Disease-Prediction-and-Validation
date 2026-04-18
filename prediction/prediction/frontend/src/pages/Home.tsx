import React from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowRight, BrainCircuit, Stethoscope, Pill, Sparkles } from 'lucide-react';


const Home: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="relative w-full flex flex-col overflow-hidden">
      {/* ─── Hero ─── */}
      <section className="relative w-full min-h-screen flex flex-col items-center justify-center px-6">


        <div className="relative z-10 max-w-4xl mx-auto text-center flex flex-col items-center">
          {/* Badge */}
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="mb-8 inline-flex items-center gap-2 px-5 py-2 rounded-full glass-panel text-[var(--neon-blue)] text-xs font-bold tracking-widest uppercase border border-[var(--neon-blue)] shadow-[0_0_10px_rgba(0,243,255,0.3)]"
          >
            <Sparkles size={14} className="text-[var(--neon-green)]" />
            Neural Engine v3.0 Online
          </motion.div>

          {/* Heading */}
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.1 }}
            className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-extrabold text-white tracking-tighter leading-[1.05] mb-6"
          >
            The Future of{' '}
            <span className="bg-gradient-to-r from-[var(--neon-blue)] via-[var(--neon-purple)] to-[var(--neon-green)] bg-clip-text text-transparent">
              AI Diagnostics
            </span>
          </motion.h1>

          {/* Subtitle */}
          <motion.p
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.3 }}
            className="text-lg md:text-xl text-gray-400 max-w-2xl leading-relaxed mb-12 font-light"
          >
            Multi-modal neural system for clinical prediction, drug validation, and explainable AI insights.
            Engineered for the next generation of healthcare.
          </motion.p>

          {/* CTAs */}
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.5 }}
            className="flex flex-col sm:flex-row gap-4"
          >
            <button
              onClick={() => navigate('/diagnosis')}
              className="group flex items-center justify-center gap-2 bg-[var(--neon-blue)] text-black font-extrabold text-sm py-4 px-10 rounded-full shadow-[0_0_20px_var(--neon-blue)] hover:shadow-[0_0_40px_var(--neon-blue)] hover:bg-white hover:-translate-y-1 transition-all duration-300 uppercase tracking-widest"
            >
              Initialize Scan
              <ArrowRight size={16} className="group-hover:translate-x-1 transition-transform" />
            </button>
            <button
              onClick={() => document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' })}
              className="flex items-center justify-center text-gray-300 font-bold text-sm py-4 px-10 rounded-full border border-white/20 hover:border-[var(--neon-purple)] hover:text-[var(--neon-purple)] hover:-translate-y-1 transition-all duration-300 uppercase tracking-widest"
            >
              Explore Systems
            </button>
          </motion.div>
        </div>

        {/* Scroll indicator */}
        <motion.div
          animate={{ y: [0, 10, 0] }}
          transition={{ duration: 2, repeat: Infinity }}
          className="absolute bottom-10 left-1/2 -translate-x-1/2 text-gray-600 text-xs uppercase tracking-widest"
        >
          <div className="w-5 h-8 rounded-full border-2 border-gray-600 flex justify-center pt-1">
            <motion.div
              animate={{ y: [0, 10, 0], opacity: [1, 0, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
              className="w-1 h-2 bg-[var(--neon-blue)] rounded-full"
            />
          </div>
        </motion.div>
      </section>

      {/* ─── Features ─── */}
      <section id="features" className="w-full py-32 relative" style={{ background: 'linear-gradient(180deg, rgba(9,10,15,0.7) 0%, rgba(10,12,21,0.5) 100%)' }}>
        <div className="container mx-auto px-6 max-w-5xl relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-80px" }}
            transition={{ duration: 0.6 }}
            className="text-center mb-20"
          >
            <h2 className="text-4xl md:text-5xl font-extrabold text-white tracking-tight">
              Engineered for{' '}
              <span className="neon-text-purple text-[var(--neon-purple)]">clinical precision.</span>
            </h2>
            <p className="text-gray-400 mt-5 text-lg max-w-xl mx-auto font-light">
              A unified neural platform combining ML ensembles, NLP, and computer vision for multi-modal analysis.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              {
                icon: <BrainCircuit size={28} strokeWidth={1.5} />,
                title: 'Neural Prediction',
                desc: 'Feed patient vitals into deep neural networks. Identify high-risk markers with transparent statistical confidence.',
                color: 'var(--neon-blue)',
              },
              {
                icon: <Stethoscope size={28} strokeWidth={1.5} />,
                title: 'Explainable AI',
                desc: 'Receive contextual breakdowns of which biometric parameters strongly influenced the algorithm\'s decision.',
                color: 'var(--neon-purple)',
              },
              {
                icon: <Pill size={28} strokeWidth={1.5} />,
                title: 'Drug Vector Analysis',
                desc: 'Automatically compare medications against prediction guidelines. Receive validated clinical suggestions.',
                color: 'var(--neon-green)',
              }
            ].map((feature, i) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 16 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-40px" }}
                transition={{ duration: 0.5, delay: i * 0.15 }}
                className="group glass-panel p-8 hover:shadow-none transition-all duration-500 relative overflow-hidden"
              >
                <div 
                  className="mb-6 inline-flex p-3.5 rounded-xl border"
                  style={{ borderColor: feature.color, color: feature.color, boxShadow: `0 0 12px ${feature.color}40` }}
                >
                  {feature.icon}
                </div>
                <h3 className="text-lg font-bold text-white mb-3 uppercase tracking-wider">{feature.title}</h3>
                <p className="text-sm text-gray-400 leading-relaxed">{feature.desc}</p>

                {/* Hover glow accent */}
                <div 
                  className="absolute -bottom-20 -right-20 w-40 h-40 rounded-full blur-3xl opacity-0 group-hover:opacity-20 transition-opacity duration-700"
                  style={{ backgroundColor: feature.color }}
                />
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── CTA Footer ─── */}
      <section className="w-full py-24 text-center relative overflow-hidden" style={{ background: 'radial-gradient(ellipse at center, rgba(13,15,24,0.6) 0%, rgba(9,10,15,0.5) 100%)' }}>
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="relative z-10"
        >
          <h2 className="text-3xl md:text-4xl font-extrabold text-white mb-4 tracking-tight">
            Ready to <span className="neon-text-green text-[var(--neon-green)]">interface</span>?
          </h2>
          <p className="text-gray-500 mb-8 max-w-md mx-auto">Begin your diagnostic session with the neural engine.</p>
          <button
            onClick={() => navigate('/diagnosis')}
            className="bg-[var(--neon-green)] text-black font-extrabold py-4 px-10 rounded-full shadow-[0_0_20px_rgba(57,255,20,0.5)] hover:shadow-[0_0_40px_rgba(57,255,20,0.8)] hover:-translate-y-1 transition-all duration-300 uppercase tracking-widest"
          >
            Launch Terminal
          </button>
        </motion.div>
      </section>
    </div>
  );
};

export default Home;

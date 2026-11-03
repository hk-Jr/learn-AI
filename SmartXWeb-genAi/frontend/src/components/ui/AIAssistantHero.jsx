import React, { useState } from 'react';
import {
  BookOpen,
  Code,
  PenTool,
  Search,
  BrainCircuit,
  Sparkles,
  ArrowRight
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export function AIAssistantHero({ onSelectPrompt, onToggleSearch, searchActive }) {
  const [activeCategory, setActiveCategory] = useState(null);

  const commandSuggestions = {
    learn: [
      "Summarize the key principles across the uploaded documents",
      "Explain the methodology and architecture details",
      "What are the main experimental or technical results?"
    ],
    code: [
      "Find code or algorithm specifications mentioned in the documents",
      "Extract API parameters, configurations, and schemas",
      "What are the software requirements and system constraints?"
    ],
    write: [
      "Draft an executive briefing based on the ingested documentation",
      "Create a quick question-and-answer guide from the sources",
      "Summarize the security and compliance policies"
    ],
  };

  return (
    <div className="d-flex flex-column align-items-center justify-content-center text-center py-4 w-100" style={{ maxWidth: '720px', margin: '0 auto' }}>
      {/* Animated Gradient Logo from Reference */}
      <div className="mb-4" style={{ width: '72px', height: '72px', position: 'relative' }}>
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 200 200"
          width="100%"
          height="100%"
        >
          <g clipPath="url(#cs_clip_1_ellipse-12)">
            <mask
              id="cs_mask_1_ellipse-12"
              style={{ maskType: "alpha" }}
              width="200"
              height="200"
              x="0"
              y="0"
              maskUnits="userSpaceOnUse"
            >
              <path
                fill="#fff"
                fillRule="evenodd"
                d="M100 150c27.614 0 50-22.386 50-50s-22.386-50-50-50-50 22.386-50 50 22.386 50 50 50zm0 50c55.228 0 100-44.772 100-100S155.228 0 100 0 0 44.772 0 100s44.772 100 100 100z"
                clipRule="evenodd"
              />
            </mask>
            <g mask="url(#cs_mask_1_ellipse-12)">
              <path fill="#fff" d="M200 0H0v200h200V0z" />
              <path fill="#0066FF" fillOpacity="0.33" d="M200 0H0v200h200V0z" />
              <g filter="url(#filter0_f_844_2811)" className="animate-gradient">
                <path fill="#0066FF" d="M110 32H18v68h92V32z" />
                <path fill="#0044FF" d="M188-24H15v98h173v-98z" />
                <path fill="#0099FF" d="M175 70H5v156h170V70z" />
                <path fill="#00CCFF" d="M230 51H100v103h130V51z" />
              </g>
            </g>
          </g>
          <defs>
            <filter
              id="filter0_f_844_2811"
              width="385"
              height="410"
              x="-75"
              y="-104"
              colorInterpolationFilters="sRGB"
              filterUnits="userSpaceOnUse"
            >
              <feFlood floodOpacity="0" result="BackgroundImageFix" />
              <feBlend in="SourceGraphic" in2="BackgroundImageFix" result="shape" />
              <feGaussianBlur result="effect1_foregroundBlur_844_2811" stdDeviation="40" />
            </filter>
            <clipPath id="cs_clip_1_ellipse-12">
              <path fill="#fff" d="M0 0H200V200H0z" />
            </clipPath>
          </defs>
        </svg>
      </div>

      {/* Header text with elegant gradient */}
      <h2 className="fw-bold mb-2" style={{
        background: 'linear-gradient(135deg, #2563eb 0%, #3b82f6 100%)',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
        fontSize: '26px',
        letterSpacing: '-0.02em'
      }}>
        Ready to assist you
      </h2>
      <p className="text-muted mb-4" style={{ fontSize: '13.5px', maxWidth: '440px' }}>
        Ask questions about your uploaded documents or explore suggestions below
      </p>

      {/* Command Category Buttons */}
      <div className="w-100 d-flex gap-3 mb-3">
        <button
          type="button"
          onClick={() => setActiveCategory(activeCategory === 'learn' ? null : 'learn')}
          className={`command-btn flex-fill ${activeCategory === 'learn' ? 'active' : ''}`}
        >
          <BookOpen className="text-primary" size={20} />
          <span>Learn</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveCategory(activeCategory === 'code' ? null : 'code')}
          className={`command-btn flex-fill ${activeCategory === 'code' ? 'active' : ''}`}
        >
          <Code className="text-primary" size={20} />
          <span>Code & Specs</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveCategory(activeCategory === 'write' ? null : 'write')}
          className={`command-btn flex-fill ${activeCategory === 'write' ? 'active' : ''}`}
        >
          <PenTool className="text-primary" size={20} />
          <span>Synthesize</span>
        </button>
      </div>

      {/* Suggestions Drawer */}
      <AnimatePresence>
        {activeCategory && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="w-100 mb-3 text-start overflow-hidden"
          >
            <div className="app-card p-0" style={{ borderRadius: '12px', overflow: 'hidden' }}>
              <div className="p-3 border-bottom d-flex align-items-center justify-content-between" style={{ backgroundColor: '#f9fafb' }}>
                <span className="fw-bold text-secondary text-uppercase" style={{ fontSize: '11px', letterSpacing: '0.05em' }}>
                  {activeCategory === 'learn' ? 'Learning Prompts' : activeCategory === 'code' ? 'Code & Spec Prompts' : 'Synthesis Prompts'}
                </span>
                <span className="badge rounded-pill bg-light text-secondary border" style={{ fontSize: '10px' }}>Click to ask</span>
              </div>
              <div className="list-group list-group-flush">
                {commandSuggestions[activeCategory].map((suggestion, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => onSelectPrompt(suggestion)}
                    className="list-group-item list-group-item-action d-flex align-items-center justify-content-between py-2 px-3 border-0"
                    style={{ fontSize: '13px' }}
                  >
                    <div className="d-flex align-items-center gap-2">
                      <Sparkles size={14} className="text-primary flex-shrink-0" />
                      <span className="text-dark">{suggestion}</span>
                    </div>
                    <ArrowRight size={13} className="text-muted" />
                  </button>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}


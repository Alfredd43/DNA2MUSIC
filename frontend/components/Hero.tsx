import { Music, Dna } from 'lucide-react'

export default function Hero({ onTrySample }: { onTrySample: () => void }) {
  return (
    <section className="relative flex flex-col items-center justify-center py-16 md:py-24 bg-background-900 dark:bg-background-900 overflow-hidden">
      {/* Animated background SVG */}
      <svg className="absolute top-0 left-0 w-full h-full opacity-20 pointer-events-none" viewBox="0 0 1440 320" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path fill="#22d3ee" fillOpacity="0.2" d="M0,160L60,170.7C120,181,240,203,360,197.3C480,192,600,160,720,133.3C840,107,960,85,1080,101.3C1200,117,1320,171,1380,197.3L1440,224L1440,320L1380,320C1320,320,1200,320,1080,320C960,320,840,320,720,320C600,320,480,320,360,320C240,320,120,320,60,320L0,320Z" />
        <circle cx="1200" cy="80" r="60" fill="#3b82f6" fillOpacity="0.12" />
        <circle cx="300" cy="200" r="80" fill="#4ade80" fillOpacity="0.10" />
      </svg>
      <div className="relative z-10 flex flex-col items-center">
        <div className="flex items-center mb-6">
          <Dna className="w-14 h-14 text-dna-500 mr-3" />
          <Music className="w-14 h-14 text-primary-500" />
        </div>
        <h1 className="text-5xl md:text-6xl font-extrabold text-gray-100 mb-4 tracking-tight text-center drop-shadow-lg">
          Turn DNA into Music
        </h1>
        <p className="text-xl md:text-2xl text-gray-300 mb-8 text-center max-w-2xl">
          AI-powered sonification of your genetic code. Upload your DNA, get a symphony. Free, private, and open source.
        </p>
        <button
          onClick={onTrySample}
          className="btn-primary text-lg px-8 py-3"
        >
          Try a Sample
        </button>
      </div>
    </section>
  )
} 
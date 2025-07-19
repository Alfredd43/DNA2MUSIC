import { Music, Dna } from 'lucide-react'

export default function Navbar() {
  return (
    <nav className="sticky top-0 z-50 w-full bg-background-900 dark:bg-background-900 border-b border-border shadow-lg flex items-center justify-between px-6 py-3">
      <div className="flex items-center gap-3">
        <span className="flex items-center">
          <Dna className="w-7 h-7 text-dna-500 mr-1" />
          <Music className="w-7 h-7 text-primary-500" />
        </span>
        <span className="ml-2 text-xl font-bold tracking-tight text-gray-100">dna2music</span>
      </div>
      <div className="flex items-center gap-6">
        <a href="#about" className="text-gray-300 hover:text-accent-500 transition-colors">About</a>
        <a href="/docs/quickstart.md" className="text-gray-300 hover:text-accent-500 transition-colors" target="_blank" rel="noopener noreferrer">Docs</a>
        <a href="https://github.com/YOUR-USERNAME/dna2music" className="text-gray-300 hover:text-accent-500 transition-colors" target="_blank" rel="noopener noreferrer">GitHub</a>
      </div>
    </nav>
  )
} 
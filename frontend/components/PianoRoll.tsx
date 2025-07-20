import { useEffect, useRef } from 'react'
import { Factory } from 'vexflow'

interface Note {
  pitch: number
  start: number
  duration: number
  velocity: number
}

interface PianoRollProps {
  notes: Note[]
  onSvgReady?: (svg: string) => void
}

const PIANO_ROLL_ID = 'pianoroll-canvas'

export default function PianoRoll({ notes, onSvgReady }: PianoRollProps) {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!containerRef.current) return
    containerRef.current.innerHTML = ''

    // Convert notes to VexFlow format
    const vexNotesArr = notes
      .map(note => {
        const noteName = getNoteName(note.pitch)
        const duration = getDuration(note.duration)
        return `${noteName}/${duration}`
      })
      .filter(n => n && typeof n === 'string' && n.trim().length > 0)

    // Only draw if at least 1 valid note
    if (vexNotesArr.length < 1) return
    const vexNotes = vexNotesArr.join(', ')
    if (!vexNotes) return

    // Initialize VexFlow
    const factory = new Factory({
      renderer: { elementId: PIANO_ROLL_ID, width: 800, height: 200 }
    })
    const score = factory.EasyScore()
    const system = factory.System()
    try {
      system.addStave({
        voices: [score.voice(score.notes(vexNotes))]
      })
      factory.draw()
      // Export SVG
      const svgElem = document.getElementById(PIANO_ROLL_ID)?.querySelector('svg')
      if (svgElem && onSvgReady) {
        onSvgReady(svgElem.outerHTML)
      }
    } catch (err) {
      // If VexFlow throws, just skip drawing
    }
  }, [notes, onSvgReady])

  const getNoteName = (pitch: number): string => {
    const noteNames = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    const octave = Math.floor(pitch / 12) - 1
    const noteIndex = pitch % 12
    return `${noteNames[noteIndex]}/${octave}`
  }

  const getDuration = (duration: number): string => {
    if (duration <= 0.25) return '16'
    if (duration <= 0.5) return '8'
    if (duration <= 1) return '4'
    return '2'
  }

  return (
    <div className="bg-gray-50 rounded-lg p-4 overflow-x-auto">
      <div ref={containerRef} id={PIANO_ROLL_ID} className="min-w-full" />
      {notes.length < 1 && (
        <div className="text-center text-gray-500 py-8">
          Not enough notes to display a score
        </div>
      )}
    </div>
  )
} 
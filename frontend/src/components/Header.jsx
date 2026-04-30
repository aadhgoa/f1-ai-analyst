import { Activity } from 'lucide-react'

export default function Header() {
  return (
    <header className="max-w-4xl mx-auto mb-10 text-center">
      <div className="inline-flex items-center justify-center p-3 bg-f1-red/10 rounded-full mb-4">
        <Activity className="text-f1-red w-8 h-8" />
      </div>
      <h1 className="text-5xl font-black tracking-tighter uppercase font-sans flex items-center justify-center gap-3">
        F1 AI <span className="text-f1-red italic">Analyst</span>
      </h1>
      <p className="opacity-70 mt-3 font-medium tracking-wide">
        Advanced autonomous telemetry & race narrative generation
      </p>
    </header>
  )
}

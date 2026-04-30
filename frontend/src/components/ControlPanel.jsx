import { Calendar, Flag, ChevronsRight, Gauge, Car } from 'lucide-react'

const YEARS = ['2026', '2025', '2024', '2023', '2022', '2021', '2020'];
const RACES = [
  'Abu Dhabi', 'Australia', 'Austria', 'Azerbaijan', 'Bahrain', 'Belgium', 
  'Brazil', 'Canada', 'China', 'Great Britain', 'Hungary', 'Imola', 'Italy', 
  'Japan', 'Las Vegas', 'Mexico', 'Miami', 'Monaco', 'Netherlands', 'Qatar', 
  'Saudi Arabia', 'Singapore', 'Spain', 'USA'
];

export default function ControlPanel({ year, setYear, gp, setGp, analyzeRace, loading, dashLoading }) {
  return (
    <section className="max-w-4xl mx-auto bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-xl shadow-2xl mb-12 flex flex-col sm:flex-row items-center justify-between gap-6">
      <div className="flex w-full items-center gap-4">
        <div className="flex-1">
          <label className="block text-xs uppercase tracking-wider font-bold mb-2 opacity-50 flex items-center gap-2">
            <Calendar className="w-4 h-4" /> Season
          </label>
          <select 
            value={year}
            onChange={(e) => setYear(e.target.value)}
            className="w-full bg-zinc-900 border border-white/10 rounded-lg px-4 py-3 text-lg font-medium focus:ring-2 focus:ring-f1-red focus:border-transparent outline-none transition-all cursor-pointer"
          >
            {YEARS.map(y => <option key={y} value={y}>{y}</option>)}
          </select>
        </div>

        <div className="flex-1 text-center hidden sm:flex items-center justify-center pt-6 opacity-30">
          <ChevronsRight className="w-8 h-8" />
        </div>

        <div className="flex-1">
          <label className="block text-xs uppercase tracking-wider font-bold mb-2 opacity-50 flex items-center gap-2">
            <Flag className="w-4 h-4" /> Grand Prix
          </label>
          <select 
            value={gp}
            onChange={(e) => setGp(e.target.value)}
            className="w-full bg-zinc-900 border border-white/10 rounded-lg px-4 py-3 text-lg font-medium focus:ring-2 focus:ring-f1-red focus:border-transparent outline-none transition-all cursor-pointer"
          >
            {RACES.map(r => <option key={r} value={r}>{r}</option>)}
          </select>
        </div>
      </div>

      <button 
        onClick={analyzeRace}
        disabled={loading || dashLoading}
        className="w-full sm:w-auto mt-6 sm:mt-0 whitespace-nowrap bg-f1-red hover:bg-red-700 text-white font-bold py-4 px-8 rounded-lg shadow-[0_0_30px_-5px_#FF1801] hover:shadow-[0_0_40px_-5px_#FF1801] transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-3 active:scale-95 border-b-4 border-black/20"
      >
        {loading ? (
          <span className="flex items-center gap-2">
             <Gauge className="w-5 h-5 animate-spin" /> Fetching...
          </span>
        ) : (
           <span className="flex items-center gap-2">
             Analyze Race <Car className="w-5 h-5" />
           </span>
        )}
      </button>
    </section>
  )
}

import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Activity, Flag, Calendar, Car, Trophy, ChevronsRight, Search, Gauge, FastForward, Timer } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import './index.css'

const YEARS = ['2026', '2025', '2024', '2023', '2022', '2021', '2020'];
const RACES = [
  'Abu Dhabi', 'Australia', 'Austria', 'Azerbaijan', 'Bahrain', 'Belgium', 
  'Brazil', 'Canada', 'China', 'Great Britain', 'Hungary', 'Imola', 'Italy', 
  'Japan', 'Las Vegas', 'Mexico', 'Miami', 'Monaco', 'Netherlands', 'Qatar', 
  'Saudi Arabia', 'Singapore', 'Spain', 'USA'
];

// Custom Tooltip for the Recharts graph
const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-black/80 backdrop-blur-md border border-white/10 p-3 rounded-lg shadow-xl text-sm">
        <p className="font-bold mb-2">Lap {label}</p>
        {payload.sort((a,b)=>a.value - b.value).map((entry, index) => (
          <div key={index} className="flex items-center gap-2 mb-1">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: entry.color }}></div>
            <span className="font-mono w-10">{entry.name}</span>
            <span className="font-bold">P{entry.value}</span>
          </div>
        ))}
      </div>
    );
  }
  return null;
};

function App() {
  const [year, setYear] = useState('2024')
  const [gp, setGp] = useState('Japan')
  
  const [loading, setLoading] = useState(false)
  const [report, setReport] = useState(null)
  const [error, setError] = useState(null)

  const [dashData, setDashData] = useState(null)
  const [dashLoading, setDashLoading] = useState(false)
  const [dashError, setDashError] = useState(null)

  const analyzeRace = () => {
    setDashLoading(true)
    setDashError(null)
    setDashData(null)
    
    setLoading(true)
    setError(null)
    setReport(null)

    fetchDashboardData()
    fetchRaceReport()
  }

  const fetchDashboardData = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/dashboard-data?year=${year}&gp=${gp}`)
      if (!response.ok) throw new Error('Failed to load telemetry dashboard')
      const data = await response.json()
      setDashData(data)
    } catch (err) {
      setDashError(err.message)
    } finally {
      setDashLoading(false)
    }
  }

  const fetchRaceReport = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/race-summary?year=${year}&gp=${gp}`)
      if (!response.ok) throw new Error('Agent failed to complete race analysis')
      const data = await response.json()
      setReport(data.summary)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen pt-8 pb-16 px-4 sm:px-8">
      
      {/* HEADER */}
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

      {/* CONTROL PANEL */}
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

      <main className="max-w-5xl mx-auto space-y-12">
        
        {/* DASHBOARD: Render Instantly once dashData is ready */}
        {dashLoading && !dashData && (
          <div className="flex justify-center items-center py-10 opacity-50">
             <Activity className="w-6 h-6 animate-pulse text-f1-red" />
          </div>
        )}

        {dashError && (
          <div className="bg-red-950/40 border border-red-500/50 p-4 rounded-xl text-red-200">
            Failed to load dashboard: {dashError}
          </div>
        )}

        {dashData && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 animate-fade-in">
            {/* Podium */}
            <div className="col-span-1 md:col-span-1 bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-md">
              <h3 className="text-xl font-black uppercase text-white/90 mb-4 flex items-center gap-2">
                <Trophy className="w-5 h-5 text-yellow-500" /> Podium
              </h3>
              <div className="space-y-4">
                {dashData.podium.map((p, i) => (
                  <div key={i} className="flex items-center justify-between p-3 bg-black/40 rounded-xl border border-white/5">
                    <div className="flex items-center gap-3">
                      <span className={`font-black text-xl w-6 ${i===0 ? 'text-yellow-500' : i===1 ? 'text-gray-300' : 'text-amber-600'}`}>{p.position}</span>
                      <div className="w-1 h-8 rounded-full" style={{ backgroundColor: p.color }}></div>
                      <div>
                        <div className="font-bold tracking-tight text-white">{p.name}</div>
                        <div className="text-xs uppercase opacity-50 tracking-wider font-mono">{p.team}</div>
                      </div>
                    </div>
                    <div className="text-sm font-mono opacity-80">{p.time}</div>
                  </div>
                ))}
              </div>

              {/* Fastest Lap */}
              <div className="mt-6 pt-6 border-t border-white/10">
                <h3 className="text-sm font-black uppercase text-f1-red/80 mb-3 flex items-center gap-2">
                   <Timer className="w-4 h-4" /> Fastest Lap
                </h3>
                <div className="p-4 bg-f1-red/10 border border-f1-red/20 rounded-xl flex items-center justify-between">
                  <div>
                    <div className="font-black text-xl text-white">{dashData.fastest_lap.driver}</div>
                    <div className="text-xs font-mono opacity-70 mt-1">Lap {dashData.fastest_lap.lap_number}</div>
                  </div>
                  <div className="text-lg font-mono font-bold text-f1-red">
                    {dashData.fastest_lap.lap_time}
                  </div>
                </div>
              </div>
            </div>

            {/* Standings Chart */}
            <div className="col-span-1 md:col-span-2 bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-md flex flex-col">
              <h3 className="text-xl font-black uppercase text-white/90 mb-6 flex items-center gap-2">
                <FastForward className="w-5 h-5 text-blue-400" /> Driver Standings
              </h3>
              <div className="flex-1 w-full min-h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={dashData.chart_data} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
                    <XAxis dataKey="lap" stroke="#ffffff50" fontSize={12} tickLine={false} axisLine={false} />
                    <YAxis reversed stroke="#ffffff50" fontSize={12} tickLine={false} axisLine={false} domain={[1, 20]} ticks={[1, 5, 10, 15, 20]} />
                    <Tooltip content={<CustomTooltip />} />
                    {Object.entries(dashData.drivers).map(([abbr, t]) => (
                      <Line 
                        key={abbr} 
                        type="stepAfter" 
                        dataKey={abbr} 
                        name={abbr} 
                        stroke={t.color} 
                        strokeWidth={2}
                        dot={false}
                        activeDot={{ r: 5 }}
                      />
                    ))}
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}

        {/* AI REPORT ZONE */}
        {loading && (
          <div className="flex flex-col items-center justify-center py-20 bg-white/5 border border-white/5 rounded-3xl mt-8">
            <div className="w-20 h-20 rounded-full bg-f1-red/20 flex items-center justify-center animate-pulse-ring mb-8">
              <Activity className="w-10 h-10 text-f1-red" />
            </div>
            <h2 className="text-2xl font-bold mb-2">Generating LLM Report...</h2>
            <p className="text-slate-400 opacity-80 flex items-center gap-2 max-w-sm text-center">
              Our agent is orchestrating MCP tools to cross-reference track statuses and fetch telemetry sweeps!
            </p>
            <div className="mt-8 flex gap-2">
               <div className="w-2 h-2 bg-f1-red rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
               <div className="w-2 h-2 bg-f1-red rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
               <div className="w-2 h-2 bg-f1-red rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
            </div>
          </div>
        )}

        {error && (
          <div className="bg-red-950/40 border border-f1-red/50 text-red-200 p-6 rounded-xl flex items-start gap-4 mt-8">
            <Trophy className="w-6 h-6 text-f1-red shrink-0" />
            <div>
              <h3 className="font-bold text-lg mb-1">Analysis Failed</h3>
              <p>{error}</p>
            </div>
          </div>
        )}

        {report && !loading && (
          <div className="bg-[#151515] border border-white/10 rounded-3xl p-8 sm:p-12 shadow-2xl relative overflow-hidden mt-8">
             <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-f1-red to-transparent opacity-50"></div>
             
             <div className="flex items-center gap-4 mb-8 pb-8 border-b border-white/10">
                <Search className="w-8 h-8 text-f1-red" />
                <div>
                  <h2 className="text-3xl font-black uppercase tracking-tight">Race Narrative</h2>
                  <p className="text-sm tracking-widest text-[#00D2BE] font-mono mt-1">DEEP DIVE COMPLETE</p>
                </div>
             </div>

             <div className="prose">
               <ReactMarkdown remarkPlugins={[remarkGfm]}>{report}</ReactMarkdown>
             </div>
          </div>
        )}

        {/* Initial Empty State */}
        {!dashData && !dashLoading && !report && !loading && !error && (
          <div className="text-center py-20 opacity-30 select-none">
             <Trophy className="w-24 h-24 mx-auto mb-6" />
             <h3 className="text-2xl font-bold uppercase tracking-widest">Awaiting Grid Start</h3>
             <p className="font-mono text-sm mt-3">Select year & Grand Prix to inspect telemetry.</p>
          </div>
        )}

      </main>

    </div>
  )
}

export default App

import { Trophy, Timer, FastForward, Activity } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

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

export default function Dashboard({ dashData, dashLoading, dashError }) {
  if (dashLoading && !dashData) {
    return (
      <div className="flex justify-center items-center py-10 opacity-50">
         <Activity className="w-6 h-6 animate-pulse text-f1-red" />
      </div>
    );
  }

  if (dashError) {
    return (
      <div className="bg-red-950/40 border border-red-500/50 p-4 rounded-xl text-red-200">
        Failed to load dashboard: {dashError}
      </div>
    );
  }

  if (!dashData) return null;

  return (
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
  );
}

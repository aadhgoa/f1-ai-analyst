import { Activity, Trophy, Search } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

export default function ReportZone({ loading, error, report }) {
  if (loading) {
    return (
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
    );
  }

  if (error) {
    return (
      <div className="bg-red-950/40 border border-f1-red/50 text-red-200 p-6 rounded-xl flex items-start gap-4 mt-8">
        <Trophy className="w-6 h-6 text-f1-red shrink-0" />
        <div>
          <h3 className="font-bold text-lg mb-1">Analysis Failed</h3>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  if (report) {
    return (
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
    );
  }

  return null;
}

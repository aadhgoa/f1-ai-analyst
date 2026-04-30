import { Trophy } from 'lucide-react'

export default function EmptyState({ dashData, dashLoading, report, loading, error }) {
  if (!dashData && !dashLoading && !report && !loading && !error) {
    return (
      <div className="text-center py-20 opacity-30 select-none">
         <Trophy className="w-24 h-24 mx-auto mb-6" />
         <h3 className="text-2xl font-bold uppercase tracking-widest">Awaiting Grid Start</h3>
         <p className="font-mono text-sm mt-3">Select year & Grand Prix to inspect telemetry.</p>
      </div>
    );
  }
  
  return null;
}

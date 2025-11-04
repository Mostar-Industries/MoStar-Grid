import React from 'react';
import { Sparkline } from "./Sparkline";

export function KpiCard({
  title, value, unit, history
}: { title: string; value: string; unit?: string; history: number[] }) {
  return (
    <div className="rounded-xl border border-white/10 bg-gradient-to-br from-purple-500/10 to-indigo-500/10 p-4">
      <div className="text-sm text-white/70">{title}</div>
      <div className="mt-1 text-2xl font-semibold text-white">{value}{unit ? <span className="text-base text-white/60 ml-1">{unit}</span> : null}</div>
      <div className="mt-2 text-white/80"><Sparkline data={history} /></div>
    </div>
  );
}

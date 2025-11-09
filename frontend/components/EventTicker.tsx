import React from 'react';
// Fix: Corrected the import path for EventPayload to point to the central types file.
import { EventPayload } from '../types';

export function EventTicker({ items }: { items: EventPayload[] }) {
  const color = (lvl: string) =>
    lvl === "info" ? "text-cyan-400" : lvl === "warn" ? "text-amber-300" : "text-rose-400";
  return (
    <div className="rounded-xl border border-white/10 bg-black/30 p-2 flex-grow min-h-0 overflow-y-auto">
      {items.length === 0 ? <div className="text-white/50 text-sm p-2 text-center">Awaiting event stream...</div> : null}
      {items.map((e, i) => (
        <div key={i} className="text-sm flex gap-3 py-1 font-mono">
          <span className="text-xs text-white/40 flex-shrink-0">{new Date(e.ts).toLocaleTimeString()}</span>
          <span className={`text-xs ${color(e.level)} w-12 uppercase flex-shrink-0`}>[{e.level}]</span>
          <span className="text-white/80 break-all">{e.text}</span>
        </div>
      ))}
    </div>
  );
}
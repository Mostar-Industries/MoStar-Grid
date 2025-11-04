import React from 'react';
import { Sparkline } from "./Sparkline";

export function ServiceHealthCard({
  name, status, rps, p50, p95, errorRate, uptime, version, history
}: {
  name: string; status: "ok" | "warn" | "fail"; rps: number; p50: number; p95: number;
  errorRate: number; uptime: number; version?: string; history: number[];
}) {
  const badge = status === "ok" ? "bg-emerald-500/20 text-emerald-300"
              : status === "warn" ? "bg-amber-500/20 text-amber-300"
              : "bg-rose-500/20 text-rose-300";
  const errPct = Math.round(errorRate * 1000) / 10;

  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-4 flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <div className="font-semibold text-white">{name}{version ? <span className="ml-2 text-xs text-white/60">v{version}</span> : null}</div>
        <span className={`px-2 py-0.5 text-xs rounded ${badge}`}>{status.toUpperCase()}</span>
      </div>
      <div className="grid grid-cols-4 gap-3 text-sm">
        <Metric label="RPS" value={rps.toFixed(1)} />
        <Metric label="p50" value={`${Math.round(p50)}ms`} />
        <Metric label="p95" value={`${Math.round(p95)}ms`} />
        <Metric label="Errors" value={`${errPct}%`} />
      </div>
      <div className="flex items-center justify-between">
        <div className="text-xs text-white/60">Uptime: {formatUptime(uptime)}</div>
        <div className="text-white/70">
          <Sparkline data={history} />
        </div>
      </div>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg bg-black/30 border border-white/10 p-2 text-center">
      <div className="text-[11px] text-white/60">{label}</div>
      <div className="text-white font-semibold">{value}</div>
    </div>
  );
}

function formatUptime(s: number) {
  if (s < 60) return `${Math.floor(s)}s`;
  const d = Math.floor(s / 86400);
  const h = Math.floor((s % 86400) / 3600);
  const m = Math.floor((s % 3600) / 60);
  if (d > 0) return `${d}d ${h}h`;
  return `${h}h ${m}m`;
}
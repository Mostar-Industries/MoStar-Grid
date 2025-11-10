import React from 'react';
import { Sparkline } from "./Sparkline";
// FIX: Import ServiceStatus type for consistency and to fix prop type issues.
import { ServiceStatus } from '../types';

const getMetricColorGradient = (value: number, min: number, max: number, higherIsBetter = true): string => {
    const range = max - min;
    if (range <= 0) return 'text-white'; // Neutral color if no range or invalid range
    
    const normalized = Math.max(0, Math.min(1, (value - min) / range));
    const score = higherIsBetter ? normalized : 1 - normalized;
    
    let gradientClass = '';
    if (score > 0.75) {
        gradientClass = 'bg-gradient-to-r from-green-400 to-emerald-400';
    } else if (score > 0.4) {
        gradientClass = 'bg-gradient-to-r from-yellow-400 to-amber-400';
    } else {
        gradientClass = 'bg-gradient-to-r from-red-400 to-rose-400';
    }

    return `bg-clip-text text-transparent ${gradientClass}`;
};

// FIX: Define a props interface for the component to resolve issues with the 'key' prop in TypeScript.
interface ServiceHealthCardProps {
  name: string;
  status: ServiceStatus;
  rps: number;
  p50: number;
  p95: number;
  errorRate: number;
  uptime: number;
  version?: string;
  history: number[];
}

// FIX: Change component to a React.FC using the defined props interface.
export const ServiceHealthCard: React.FC<ServiceHealthCardProps> = ({
  name, status, rps, p50, p95, errorRate, uptime, version, history
}) => {
  const badge = status === "ok" ? "bg-emerald-500/20 text-emerald-300"
              : status === "warn" ? "bg-amber-500/20 text-amber-300"
              : "bg-rose-500/20 text-rose-300";
  const errPct = Math.round(errorRate * 1000) / 10;

  const rpsColor = getMetricColorGradient(rps, 50, 150, true);
  const p50Color = getMetricColorGradient(p50, 20, 70, false);
  const p95Color = getMetricColorGradient(p95, 40, 150, false);
  const errorColor = getMetricColorGradient(errorRate, 0, 0.1, false);

  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-4 flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <div className="font-semibold text-white">{name}{version ? <span className="ml-2 text-xs text-white/60">v{version}</span> : null}</div>
        <span className={`px-2 py-0.5 text-xs rounded ${badge}`}>{status.toUpperCase()}</span>
      </div>
      <div className="grid grid-cols-4 gap-3 text-sm">
        <Metric label="RPS" value={rps.toFixed(1)} valueColorClass={rpsColor} />
        <Metric label="p50" value={`${Math.round(p50)}`} unit="ms" valueColorClass={p50Color} />
        <Metric label="p95" value={`${Math.round(p95)}`} unit="ms" valueColorClass={p95Color} />
        <Metric label="Errors" value={`${errPct}`} unit="%" valueColorClass={errorColor} />
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

function Metric({ label, value, unit, valueColorClass = 'text-white' }: { label: string; value: string; unit?: string; valueColorClass?: string; }) {
  return (
    <div className="rounded-lg bg-black/30 border border-white/10 p-2 text-center">
      <div className="text-[11px] text-white/60">{label}</div>
      <div className="text-white font-semibold">
        <span className={valueColorClass}>{value}</span>
        {unit && <span className="text-sm text-white/60">{unit}</span>}
      </div>
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
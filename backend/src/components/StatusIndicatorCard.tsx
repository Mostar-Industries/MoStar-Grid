import React from 'react';

interface StatusIndicatorCardProps {
  title: string;
  status: 'Online' | 'Offline' | 'Checking...';
  description: string;
  lastChecked?: Date | null;
}

export const StatusIndicatorCard: React.FC<StatusIndicatorCardProps> = ({ title, status, description, lastChecked }) => {
    const colors = status === 'Online' 
        ? { badge: 'bg-emerald-500/20 text-emerald-300', icon: 'fa-check-circle' }
        : status === 'Offline'
        ? { badge: 'bg-rose-500/20 text-rose-300', icon: 'fa-times-circle' }
        : { badge: 'bg-amber-500/20 text-amber-300', icon: 'fa-spinner fa-spin' };

    return (
        <div className="rounded-xl border border-white/10 bg-white/5 p-4 flex flex-col gap-3 h-full">
            <div className="flex items-center justify-between">
                <div className="font-semibold text-white">{title}</div>
                <span className={`px-2 py-0.5 text-xs rounded ${colors.badge} flex items-center`}>
                    <i className={`fas ${colors.icon} mr-1.5`}></i>
                    {status.toUpperCase()}
                </span>
            </div>
            <p className="text-sm text-white/70 flex-grow">{description}</p>
            <div className="text-xs text-white/40 mt-auto">
                {lastChecked ? `Last check: ${lastChecked.toLocaleTimeString()}` : 'Awaiting first check...'}
            </div>
        </div>
    );
}
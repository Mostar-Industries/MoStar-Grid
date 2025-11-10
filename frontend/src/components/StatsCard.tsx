
import React from 'react';
import { StatsCardData } from '../types';

const colorClasses = {
    purple: { bg: 'bg-purple-500/20', text: 'text-purple-300' },
    blue: { bg: 'bg-sky-500/20', text: 'text-sky-300' },
    green: { bg: 'bg-emerald-500/20', text: 'text-emerald-300' },
    yellow: { bg: 'bg-amber-500/20', text: 'text-amber-300' },
    teal: { bg: 'bg-teal-500/20', text: 'text-teal-300' },
    red: { bg: 'bg-rose-500/20', text: 'text-rose-300' },
    indigo: { bg: 'bg-indigo-500/20', text: 'text-indigo-300' },
    pink: { bg: 'bg-pink-500/20', text: 'text-pink-300' },
};

const StatsCard: React.FC<StatsCardData & { valueColorClass?: string }> = ({ title, value, icon, color, valueColorClass = 'text-white' }) => {
    const colors = colorClasses[color] || colorClasses.purple;

    return (
        <div className="grid-card rounded-lg shadow p-4">
            <div className="flex items-start justify-between mb-3">
                <div>
                    <p className="text-gray-400 text-sm">{title}</p>
                    <h3 className={`text-2xl font-bold ${valueColorClass}`}>{value}</h3>
                </div>
                <div className={`p-3 rounded-full ${colors.bg} ${colors.text}`}>
                    <i className={`fas ${icon}`}></i>
                </div>
            </div>
        </div>
    );
};

export default StatsCard;
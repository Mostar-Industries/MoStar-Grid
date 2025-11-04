
import React from 'react';
import { StatsCardData } from '../types';

const colorClasses = {
    purple: { bg: 'bg-purple-900', text: 'text-purple-400' },
    blue: { bg: 'bg-blue-900', text: 'text-blue-400' },
    green: { bg: 'bg-green-900', text: 'text-green-400' },
    yellow: { bg: 'bg-yellow-900', text: 'text-yellow-400' },
    teal: { bg: 'bg-teal-900', text: 'text-teal-400' },
};

const StatsCard: React.FC<StatsCardData> = ({ title, value, icon, color }) => {
    const colors = colorClasses[color] || colorClasses.purple;

    return (
        <div className="grid-card rounded-sl shadow p-4">
            <div className="flex items-start justify-between mb-3">
                <div>
                    <p className="text-gray-400 text-sm">{title}</p>
                    <h3 className="text-2xl font-bold text-white">{value}</h3>
                </div>
                <div className={`p-3 rounded-full ${colors.bg} ${colors.text}`}>
                    <i className={`fas ${icon}`}></i>
                </div>
            </div>
        </div>
    );
};

export default StatsCard;

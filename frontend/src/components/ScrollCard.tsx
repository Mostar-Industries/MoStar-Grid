import React from 'react';
import { Scroll } from '../types/moscript';
import { Interpretation } from '../lib/mostar/WooInterpreter';

interface ScrollCardProps {
    scroll: Scroll;
    interpretation: Interpretation;
    onRun: (scroll: Scroll) => void;
    isSentinelMode: boolean;
}

const statusColors = {
    approved: { border: 'border-green-500', text: 'text-green-400', bg: 'bg-green-900/50' },
    warning: { border: 'border-yellow-500', text: 'text-yellow-400', bg: 'bg-yellow-900/50' },
    denied: { border: 'border-red-500', text: 'text-red-400', bg: 'bg-red-900/50' },
};

const ScrollCard: React.FC<ScrollCardProps> = ({ scroll, interpretation, onRun, isSentinelMode }) => {
    const colors = statusColors[interpretation.status];
    const scorePercent = (interpretation.score * 100).toFixed(2);

    return (
        <div className={`grid-card rounded-lg shadow p-4 flex flex-col border-l-4 ${colors.border} ${colors.bg}`}>
            <div className="flex items-start justify-between mb-3">
                <div className="flex items-center">
                    <div className={`p-2 rounded-lg mr-3 ${colors.text}`}>
                        <i className="fas fa-file-code"></i>
                    </div>
                    <div>
                        <h4 className="font-bold text-white">{scroll.name}</h4>
                        <p className="text-gray-400 text-sm">by {scroll.author}</p>
                    </div>
                </div>
                <div className={`px-2 py-1 ${colors.bg} ${colors.text} text-xs rounded-full`}>
                    {interpretation.status.toUpperCase()}
                </div>
            </div>
            <p className="text-gray-300 text-sm mb-3 flex-grow">{scroll.description}</p>
            <div className="text-xs text-gray-500 mb-3">
                <p>Resonance Score: <span className={colors.text}>{scorePercent}%</span></p>
                <p className="italic">Woo: "{interpretation.proverb}"</p>
            </div>
            <div className="mt-auto">
                <button
                    onClick={() => onRun(scroll)}
                    disabled={isSentinelMode}
                    className="w-full bg-purple-600 text-white py-2 px-4 rounded-lg font-medium text-sm flex items-center justify-center hover:bg-purple-700 transition-colors disabled:bg-gray-600 disabled:cursor-not-allowed"
                >
                    <i className={`fas ${isSentinelMode ? 'fa-lock' : 'fa-play'} mr-2`}></i>
                    {isSentinelMode ? 'Execution Sealed' : 'Run Scroll'}
                </button>
            </div>
        </div>
    );
};

export default ScrollCard;
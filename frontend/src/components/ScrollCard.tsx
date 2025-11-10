import React from 'react';
import { Scroll, Interpretation } from '../types';

interface ScrollCardProps {
    scroll: Scroll;
    interpretation?: Interpretation;
    onViewDetails?: (scrollId: string) => void;
}

const ScrollCard: React.FC<ScrollCardProps> = ({ scroll, interpretation, onViewDetails }) => {
    const statusColor = interpretation 
        ? interpretation.status === 'approved' ? 'bg-green-500/20 text-green-300'
            : interpretation.status === 'warning' ? 'bg-amber-500/20 text-amber-300'
            : 'bg-red-500/20 text-red-300'
        : 'bg-gray-500/20 text-gray-300';
    
    const icon = interpretation 
        ? interpretation.status === 'approved' ? 'fa-check-circle'
            : interpretation.status === 'warning' ? 'fa-exclamation-triangle'
            : 'fa-times-circle'
        : 'fa-scroll';

    return (
        <div className="rounded-lg shadow p-4 flex flex-col bg-card border border-white/10">
            <div className="flex items-center justify-between mb-3">
                <div className="flex items-center">
                    <div className={`p-2 rounded-lg ${statusColor} mr-3`}>
                        <i className={`fas ${icon}`}></i>
                    </div>
                    <div>
                        <h4 className="font-bold text-white">{scroll.name}</h4>
                        <p className="text-gray-400 text-sm">by {scroll.author}</p>
                    </div>
                </div>
                {interpretation && (
                    <span className={`px-2 py-0.5 text-xs rounded ${statusColor}`}>
                        {interpretation.status.toUpperCase()}
                    </span>
                )}
            </div>
            <p className="text-gray-300 text-sm mb-3 flex-grow">{scroll.description}</p>
            {interpretation && (
                <div className="text-xs text-gray-500 mb-3">
                    <p><strong>Score:</strong> {(interpretation.score * 100).toFixed(1)}%</p>
                    <p><em>"{interpretation.proverb}"</em></p>
                </div>
            )}
            <div className="flex items-center justify-end text-xs text-gray-500 mt-auto">
                {onViewDetails && (
                    <button 
                        onClick={() => onViewDetails(scroll.id)}
                        className="text-blue-400 hover:text-blue-300 text-sm">
                        View MoScript <i className="fas fa-arrow-right ml-1"></i>
                    </button>
                )}
            </div>
        </div>
    );
};

export default ScrollCard;


import React from 'react';
import { KnowledgeCardData } from '../types';

const tagColorClasses = {
    purple: { bg: 'bg-purple-500/20', text: 'text-purple-300' },
    blue: { bg: 'bg-sky-500/20', text: 'text-sky-300' },
    green: { bg: 'bg-emerald-500/20', text: 'text-emerald-300' },
    yellow: { bg: 'bg-amber-500/20', text: 'text-amber-300' },
    red: { bg: 'bg-rose-500/20', text: 'text-rose-300' },
    indigo: { bg: 'bg-indigo-500/20', text: 'text-indigo-300' },
    pink: { bg: 'bg-pink-500/20', text: 'text-pink-300' },
    teal: { bg: 'bg-teal-500/20', text: 'text-teal-300' },
};

const iconColorClasses = {
    purple: 'text-purple-400 bg-purple-400/20',
    blue: 'text-sky-400 bg-sky-400/20',
    green: 'text-emerald-400 bg-emerald-400/20',
    yellow: 'text-amber-400 bg-amber-400/20',
    red: 'text-rose-400 bg-rose-400/20',
    indigo: 'text-indigo-400 bg-indigo-400/20',
    pink: 'text-pink-400 bg-pink-400/20',
    teal: 'text-teal-400 bg-teal-400/20',
};

const KnowledgeCard: React.FC<KnowledgeCardData> = ({ title, subtitle, description, icon, iconColor, tags, updated, size }) => {
    const iconColors = iconColorClasses[iconColor] || iconColorClasses.purple;
    
    return (
        <div className="grid-card rounded-lg shadow p-4 flex flex-col">
            <div className="flex items-start justify-between mb-3">
                <div className="flex items-center">
                    <div className={`p-2 rounded-lg ${iconColors} mr-3`}>
                        <i className={`fas ${icon}`}></i>
                    </div>
                    <div>
                        <h4 className="font-bold text-white">{title}</h4>
                        <p className="text-gray-400 text-sm">{subtitle}</p>
                    </div>
                </div>
                <button className="text-gray-400 hover:text-gray-200">
                    <i className="fas fa-ellipsis-v"></i>
                </button>
            </div>
            <p className="text-gray-300 text-sm mb-3 flex-grow">{description}</p>
            <div className="flex flex-wrap gap-2 mb-3">
                {tags.map(tag => {
                    const colors = tagColorClasses[tag.color] || tagColorClasses.purple;
                    return (
                        <span key={tag.name} className={`px-2 py-1 ${colors.bg} ${colors.text} text-xs rounded-full`}>
                            {tag.name}
                        </span>
                    );
                })}
            </div>
            <div className="flex items-center justify-between text-xs text-gray-500 mt-auto">
                <span>Updated {updated}</span>
                <span>{size}</span>
            </div>
        </div>
    );
};

export default KnowledgeCard;
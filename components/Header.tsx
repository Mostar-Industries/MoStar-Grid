import React from 'react';
import { Page } from '../types';

interface HeaderProps {
    onNavigate: (page: Page) => void;
    isSentinelMode: boolean;
}

const Header: React.FC<HeaderProps> = ({ onNavigate, isSentinelMode }) => {
    return (
        <header className="bg-gray-900/50 backdrop-blur-sm shadow-sm z-5 border-b border-gray-800">
            <div className="flex items-center justify-between px-6 py-4">
                <div className="flex items-center">
                    <div className="relative w-30">
                        <input type="text" placeholder="Query the Grid's memory..."
                            className="w-full pl-10 pr-4 py-2 rounded-lg border border-gray-700 bg-gray-800 text-white focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent" />
                        <i className="fas fa-search absolute left-3 top-3 text-gray-400"></i>
                    </div>
                </div>

                <div className="flex items-center space-x-4">
                    {isSentinelMode && (
                        <div className="flex items-center space-x-2 text-cyan-400 animate-pulse">
                            <i className="fas fa-shield-alt"></i>
                            <span className="text-sm font-medium">Sentinel Mode</span>
                        </div>
                    )}
                    <button 
                        onClick={() => onNavigate('forge')}
                        className="pulse-animation gradient-bg text-white py-2 px-4 rounded-lg font-medium flex items-center hover:opacity-90 transition-opacity">
                        <i className="fas fa-hammer mr-2"></i>
                        Enter The Forge
                    </button>
                    <div className="h-8 w-8 rounded-full gradient-bg flex items-center justify-center text-white font-bold cursor-pointer">
                        <i className="fas fa-user-astronaut"></i>
                    </div>
                </div>
            </div>
        </header>
    );
};

export default Header;
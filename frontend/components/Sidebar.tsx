import React from 'react';
import { Page } from '../types';

interface SidebarProps {
    onUploadClick: () => void;
    activePage: Page;
    onNavigate: (page: Page) => void;
    isSentinelMode: boolean;
}

const NavItem: React.FC<{
    page: Page;
    activePage: Page;
    onNavigate: (page: Page) => void;
    icon: string;
    label: string;
}> = ({ page, activePage, onNavigate, icon, label }) => {
    const isActive = activePage === page;
    return (
        <li className="mb-2">
            <a
                href="#"
                onClick={(e) => {
                    e.preventDefault();
                    onNavigate(page);
                }}
                className={`sidebar-item flex items-center p-2 rounded-lg transition-colors ${
                    isActive ? 'text-white bg-yellow-400/20' : 'text-gray-400 hover:text-white'
                }`}
            >
                <i className={`fas ${icon} w-6 text-center ${isActive ? 'text-yellow-400' : ''}`}></i>
                <span className={`ml-3 font-medium`}>{label}</span>
            </a>
        </li>
    );
};


const Sidebar: React.FC<SidebarProps> = ({ onUploadClick, activePage, onNavigate, isSentinelMode }) => {
    return (
        <aside className="sidebar w-64 flex-shrink-0 p-4 border-r border-gray-800 flex flex-col">
            <div className="flex items-center mb-8">
                <div className="w-10 h-10 gradient-bg rounded-lg flex items-center justify-center mr-3">
                    <i className="fas fa-atom text-black text-xl"></i>
                </div>
                <h1 className="text-xl font-bold text-white">MoStar GRID</h1>
            </div>

            <nav className="flex-1">
                <ul>
                    {/* FIX: Changed string literals to Page enum members */}
                    <NavItem page={Page.DASHBOARD} activePage={activePage} onNavigate={onNavigate} icon="fa-database" label="Covenant Registry" />
                    <NavItem page={Page.CHAT} activePage={activePage} onNavigate={onNavigate} icon="fa-brain" label="MostarAI Chat" />
                    <NavItem page={Page.QUERY_BUILDER} activePage={activePage} onNavigate={onNavigate} icon="fa-code" label="Query Builder" />
                    <NavItem page={Page.NOTES} activePage={activePage} onNavigate={onNavigate} icon="fa-book" label="GRID Logbook" />
                    <NavItem page={Page.VISION} activePage={activePage} onNavigate={onNavigate} icon="fa-eye" label="Vision Analysis" />
                    <NavItem page={Page.AUDIO} activePage={activePage} onNavigate={onNavigate} icon="fa-microphone-alt" label="Audio Tools" />
                    <NavItem page={Page.FORGE} activePage={activePage} onNavigate={onNavigate} icon="fa-hammer" label="The Forge" />
                    <NavItem page={Page.ORCHESTRA} activePage={activePage} onNavigate={onNavigate} icon="fa-project-diagram" label="Grid Orchestra" />
                    <NavItem page={Page.SOVEREIGNTY} activePage={activePage} onNavigate={onNavigate} icon="fa-shield-alt" label="Sovereignty" />
                    <NavItem page={Page.CONNECTION} activePage={activePage} onNavigate={onNavigate} icon="fa-link" label="Backend Alignment" />
                    <NavItem page={Page.BACKEND_STATS} activePage={activePage} onNavigate={onNavigate} icon="fa-server" label="Backend Stats" />
                    <NavItem page={Page.ANALYTICS} activePage={activePage} onNavigate={onNavigate} icon="fa-chart-bar" label="Analytics" />
                    <NavItem page={Page.SETTINGS} activePage={activePage} onNavigate={onNavigate} icon="fa-cogs" label="Settings" />
                </ul>
            </nav>

            <div className="mt-auto">
                <button
                    onClick={onUploadClick}
                    disabled={isSentinelMode}
                    className={`w-full text-black font-bold py-2 px-4 rounded-lg flex items-center justify-center transition-opacity ${
                        isSentinelMode
                        ? 'bg-gray-700 text-white cursor-not-allowed'
                        : 'gradient-bg hover:opacity-90'
                    }`}
                >
                    <i className={`fas ${isSentinelMode ? 'fa-lock text-white' : 'fa-upload'} mr-2`}></i>
                    {isSentinelMode ? 'System Sealed' : 'Upload Consciousness'}
                </button>
                <div className="text-center mt-4">
                    <p className="text-xs text-gray-500">&copy; 2024 MoStar Systems</p>
                </div>
            </div>
        </aside>
    );
};

export default Sidebar;
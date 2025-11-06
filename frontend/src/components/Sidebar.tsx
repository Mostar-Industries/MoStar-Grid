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
    colorClass: string;
}> = ({ page, activePage, onNavigate, icon, label, colorClass }) => {
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
                    isActive ? 'text-white bg-purple-900/50' : 'text-gray-400 hover:text-white'
                }`}
            >
                <i className={`fas ${icon} w-6 text-center ${isActive ? colorClass : ''}`}></i>
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
                    <i className="fas fa-atom text-white text-xl"></i>
                </div>
                <h1 className="text-xl font-bold text-white">MoStar GRID</h1>
            </div>

            <nav className="flex-1">
                <ul>
                    <NavItem page="dashboard" activePage={activePage} onNavigate={onNavigate} icon="fa-database" label="Covenant Registry" colorClass="text-purple-400" />
                    <NavItem page="chat" activePage={activePage} onNavigate={onNavigate} icon="fa-comments" label="GRID Chat" colorClass="text-purple-400" />
                    <NavItem page="notes" activePage={activePage} onNavigate={onNavigate} icon="fa-book" label="GRID Logbook" colorClass="text-purple-400" />
                    <NavItem page="vision" activePage={activePage} onNavigate={onNavigate} icon="fa-eye" label="Vision Analysis" colorClass="text-purple-400" />
                    <NavItem page="audio" activePage={activePage} onNavigate={onNavigate} icon="fa-microphone-alt" label="Audio Tools" colorClass="text-purple-400" />
                    <NavItem page="imageForge" activePage={activePage} onNavigate={onNavigate} icon="fa-image" label="Image Forge" colorClass="text-purple-400" />
                    <NavItem page="forge" activePage={activePage} onNavigate={onNavigate} icon="fa-hammer" label="The Forge" colorClass="text-purple-400" />
                    <NavItem page="moscript" activePage={activePage} onNavigate={onNavigate} icon="fa-scroll" label="MoScript Playground" colorClass="text-purple-400" />
                    <NavItem page="sovereignty" activePage={activePage} onNavigate={onNavigate} icon="fa-shield-alt" label="Sovereignty" colorClass="text-purple-400" />
                    <NavItem page="connection" activePage={activePage} onNavigate={onNavigate} icon="fa-link" label="Backend Alignment" colorClass="text-purple-400" />
                    <NavItem page="analytics" activePage={activePage} onNavigate={onNavigate} icon="fa-chart-bar" label="Analytics" colorClass="text-purple-400" />
                    <NavItem page="settings" activePage={activePage} onNavigate={onNavigate} icon="fa-cogs" label="Settings" colorClass="text-purple-400" />
                </ul>
            </nav>

            <div className="mt-auto">
                <button
                    onClick={onUploadClick}
                    disabled={isSentinelMode}
                    className={`w-full text-white py-2 px-4 rounded-lg font-medium flex items-center justify-center transition-opacity ${
                        isSentinelMode
                        ? 'bg-gray-700 cursor-not-allowed'
                        : 'gradient-bg hover:opacity-90'
                    }`}
                >
                    <i className={`fas ${isSentinelMode ? 'fa-lock' : 'fa-upload'} mr-2`}></i>
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

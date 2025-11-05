import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import ChatPage from './pages/ChatPage';
import VisionPage from './pages/VisionPage';
import AudioPage from './pages/AudioPage';
import ForgePage from './pages/ForgePage';
import SovereigntyPage from './pages/SovereigntyPage';
import ImageForgePage from './pages/ImageForgePage';
import MoScriptPage from './pages/MoScriptPage';
import NotesPage from './pages/NotesPage';
import ConnectionPage from './pages/ConnectionPage';
import UploadModal from './components/UploadModal';
import TrainingModal from './components/TrainingModal';
import { Page } from './types';
import { initializeCovenant } from './lib/mostar/BuilderPacket';


const App: React.FC = () => {
    const [activePage, setActivePage] = useState<Page>('dashboard');
    const [isSentinelMode, setIsSentinelMode] = useState(false);
    const [isUploadModalOpen, setUploadModalOpen] = useState(false);
    const [isTrainingModalOpen, setTrainingModalOpen] = useState(false);

    useEffect(() => {
        // Initialize core systems on startup
        initializeCovenant();
    }, []);

    const renderPage = () => {
        switch (activePage) {
            case 'dashboard':
                return <Dashboard />;
            case 'chat':
                return <ChatPage />;
            case 'vision':
                return <VisionPage isSentinelMode={isSentinelMode} />;
            case 'audio':
                return <AudioPage isSentinelMode={isSentinelMode} />;
            case 'forge':
                return <ForgePage />;
             case 'imageForge':
                return <ImageForgePage />;
            case 'moscript':
                return <MoScriptPage />;
            case 'sovereignty':
                return <SovereigntyPage isSentinelMode={isSentinelMode} setIsSentinelMode={setIsSentinelMode} />;
            case 'notes':
                return <NotesPage />;
            case 'connection':
                return <ConnectionPage />;
            // Add other pages here
            // case 'analytics':
            // case 'settings':
            default:
                // Fallback to dashboard for any page not yet implemented.
                return <Dashboard />;
        }
    };
    
    // Header button navigation
    const handleHeaderNavigate = (page: Page) => {
        if (page === 'forge') {
            setTrainingModalOpen(true);
        } else {
            setActivePage(page);
        }
    };

    return (
        <div className="flex h-screen bg-gray-900 text-gray-200 font-sans">
            <Sidebar 
                onUploadClick={() => setUploadModalOpen(true)} 
                activePage={activePage} 
                onNavigate={setActivePage} // Sidebar directly sets the page
                isSentinelMode={isSentinelMode}
            />
            <div className="flex-1 flex flex-col overflow-hidden">
                <Header onNavigate={handleHeaderNavigate} isSentinelMode={isSentinelMode} />
                <main className="flex-1 overflow-y-auto bg-gray-900/80">
                    {/* The main content padding is applied inside each page for better control */}
                    {renderPage()}
                </main>
            </div>
            
            <UploadModal isOpen={isUploadModalOpen} onClose={() => setUploadModalOpen(false)} />
            <TrainingModal isOpen={isTrainingModalOpen} onClose={() => setTrainingModalOpen(false)} />
        </div>
    );
};

export default App;

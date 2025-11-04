import React, { useState, useEffect } from 'react';
import { Page, StatPayload, ServicePayload, EventPayload } from './types';
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
import UploadModal from './components/UploadModal';
import TrainingModal from './components/TrainingModal';
import TickerFeed from './components/TickerFeed';
import { useSSE } from './hooks/useSSE';
import { startMetricSimulator, stopMetricSimulator } from './services/metricSimulator';

const App: React.FC = () => {
    const [activePage, setActivePage] = useState<Page>('dashboard');
    const [isSentinelMode, setIsSentinelMode] = useState(false);
    const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
    const [isTrainingModalOpen, setIsTrainingModalOpen] = useState(false);

    // Centralized SSE data management
    const { stats, services, events } = useSSE('/api/sse'); // URL is unused in mock

    useEffect(() => {
        startMetricSimulator();
        return () => {
            stopMetricSimulator();
        };
    }, []);
    
    const latestEvent = events?.[0];

    const handleNavigate = (page: Page) => {
        setActivePage(page);
    };

    const renderPage = () => {
        switch (activePage) {
            case 'dashboard':
                return <Dashboard 
                            onOpenTrainingModal={() => setIsTrainingModalOpen(true)}
                            stats={stats}
                            services={services}
                            events={events}
                            isSentinelMode={isSentinelMode}
                       />;
            case 'chat':
                return <ChatPage />;
            case 'notes':
                return <NotesPage />;
            case 'vision':
                return <VisionPage isSentinelMode={isSentinelMode} />;
            case 'audio':
                return <AudioPage isSentinelMode={isSentinelMode} />;
            case 'imageForge':
                return <ImageForgePage />;
            case 'forge':
                return <ForgePage />;
            case 'moscript':
                return <MoScriptPage />;
            case 'sovereignty':
                return <SovereigntyPage isSentinelMode={isSentinelMode} setIsSentinelMode={setIsSentinelMode} />;
            case 'analytics':
                return <div className="p-6 text-white"><h2 className="text-2xl font-bold">Analytics</h2><p>This page is under construction.</p></div>;
            case 'settings':
                 return <div className="p-6 text-white"><h2 className="text-2xl font-bold">Settings</h2><p>This page is under construction.</p></div>;
            default:
                return <Dashboard 
                            onOpenTrainingModal={() => setIsTrainingModalOpen(true)}
                            stats={stats}
                            services={services}
                            events={events}
                            isSentinelMode={isSentinelMode}
                        />;
        }
    };

    return (
        <div className="flex h-screen bg-gray-900 text-gray-100 font-sans">
            <Sidebar 
                onUploadClick={() => setIsUploadModalOpen(true)} 
                activePage={activePage} 
                onNavigate={handleNavigate}
                isSentinelMode={isSentinelMode}
            />
            <main className="flex-1 flex flex-col overflow-hidden">
                <Header onNavigate={handleNavigate} isSentinelMode={isSentinelMode} />
                <div className="flex-1 p-6 overflow-y-auto bg-gray-900/50">
                    {renderPage()}
                </div>
                <TickerFeed stats={stats} latestEvent={latestEvent} />
            </main>
            <UploadModal isOpen={isUploadModalOpen} onClose={() => setIsUploadModalOpen(false)} />
            <TrainingModal isOpen={isTrainingModalOpen} onClose={() => setIsTrainingModalOpen(false)} />
        </div>
    );
};

export default App;
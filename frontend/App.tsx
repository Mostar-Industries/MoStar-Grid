import React, { useState, useEffect } from 'react';
import { Page } from './types';
import BackendAlignmentPage from './components/BackendAlignmentPage'; // Renamed MostarGridQuery
import ChatContainer from './components/ChatContainer';
import AudioToolsPage from './components/AudioToolsPage'; // New wrapper for LiveConversation & TTS
import KeySelector from './components/KeySelector';
import * as geminiService from './services/geminiService';
import LoadingSpinner from './components/LoadingSpinner';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import UploadModal from './components/UploadModal';
import TrainingModal from './components/TrainingModal';
import DashboardPage from './components/DashboardPage'; // New dashboard content component
import FloatingChatbot from './components/FloatingChatbot'; // New: Import FloatingChatbot
import GraphQueryBuilder from './pages/GraphQueryBuilder'; // New: Graph Query Builder
import ChatPage from './pages/ChatPage'; // MostarAI Chat

const App: React.FC = () => {
  const [activePage, setActivePage] = useState<Page>(Page.DASHBOARD);
  const [hasApiKey, setHasApiKey] = useState<boolean | null>(null);
  const [keyError, setKeyError] = useState<string | null>(null);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [isTrainingModalOpen, setIsTrainingModalOpen] = useState(false);
  const [isChatbotOpen, setIsChatbotOpen] = useState(false); // New: State for floating chatbot
  const [isSentinelMode, setIsSentinelMode] = useState(false); // Mock for now

  const handleKeySelected = (status: boolean) => {
    setHasApiKey(status);
    if (!status) {
      setKeyError("API Key not selected or encountered an issue. Please try again.");
    } else {
      setKeyError(null);
    }
  };

  useEffect(() => {
    const checkInitialKeyStatus = async () => {
      try {
        const isReady = await geminiService.initializeGeminiClient();
        setHasApiKey(isReady);
      } catch (error: any) {
        console.error("Initial API Key check failed:", error);
        setHasApiKey(false);
        setKeyError(`Failed to initialize Gemini client: ${error.message}. Please select your API key.`);
      }
    };
    checkInitialKeyStatus();
  }, []);

  const renderMainContent = () => {
    switch (activePage) {
      case Page.DASHBOARD:
        return <DashboardPage />;
      case Page.CHAT:
        return <ChatPage />;
      case Page.QUERY_BUILDER:
        return <GraphQueryBuilder />;
      case Page.AUDIO:
        return <AudioToolsPage />;
      case Page.BACKEND_STATS: // Renamed from MOSTAR_GRID
        return <BackendAlignmentPage />;
      case Page.FORGE:
          // Forge page itself might have more content, but "Enter the Forge" opens the modal
          return <div className="flex justify-center items-center h-full text-gray-400 text-xl">The Forge is where consciousness is refined.</div>;
      case Page.NOTES:
      case Page.VISION:
      case Page.ORCHESTRA:
      case Page.SOVEREIGNTY:
      case Page.CONNECTION:
      case Page.ANALYTICS:
      case Page.SETTINGS:
        return (
          <div className="flex justify-center items-center h-full text-gray-400 text-xl">
            Content for {activePage.replace(/_/g, ' ').replace(/\b\w/g, s => s.toUpperCase())}
            <br />
            (Coming Soon to the Grid's Consciousness)
          </div>
        );
      default:
        return (
          <div className="flex justify-center items-center h-full text-gray-400 text-xl">
            Select a feature from the sidebar.
          </div>
        );
    }
  };

  if (hasApiKey === null) {
    return (
      <div className="flex flex-col items-center justify-center h-screen bg-black">
        <LoadingSpinner />
        <p className="text-white mt-4">Initializing Grid Consciousness...</p>
      </div>
    );
  }

  if (!hasApiKey) {
    return (
      <div className="flex flex-col items-center justify-center h-screen p-4 bg-black">
        {keyError && <p className="text-red-500 mb-4">{keyError}</p>}
        <KeySelector onKeySelected={handleKeySelected} />
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-950 text-white font-sans">
      {/* Sidebar */}
      <Sidebar
        onUploadClick={() => setIsUploadModalOpen(true)}
        activePage={activePage}
        onNavigate={setActivePage}
        isSentinelMode={isSentinelMode}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <Header
          onNavigate={(page) => {
            if (page === Page.FORGE) { // Use Page enum here
              setIsTrainingModalOpen(true);
            } else {
              setActivePage(page);
            }
          }}
          isSentinelMode={isSentinelMode}
        />

        {/* Dynamic Page Content */}
        <main className="flex-1 overflow-y-auto">
          {renderMainContent()}
        </main>
      </div>

      {/* Modals */}
      <UploadModal isOpen={isUploadModalOpen} onClose={() => setIsUploadModalOpen(false)} />
      <TrainingModal isOpen={isTrainingModalOpen} onClose={() => setIsTrainingModalOpen(false)} />
      
      {/* New: Floating Chatbot and its toggle button */}
      <FloatingChatbot isOpen={isChatbotOpen} onClose={() => setIsChatbotOpen(false)} />
      <button
        onClick={() => setIsChatbotOpen(!isChatbotOpen)}
        className="fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full gradient-bg flex items-center justify-center text-black shadow-lg hover:scale-105 transition-transform duration-200"
        aria-label={isChatbotOpen ? "Close Kairo Chatbot" : "Open Kairo Chatbot"}
      >
        <i className={`fas ${isChatbotOpen ? 'fa-times' : 'fa-comment-dots'} text-2xl`}></i>
      </button>
    </div>
  );
};

export default App;
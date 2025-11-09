import React from 'react';
import LiveConversationPanel from './LiveConversationPanel';
import TTSPanel from './TTSPanel';

const AudioToolsPage: React.FC = () => {
  return (
    <div className="flex flex-col gap-8 p-4 md:p-8 max-w-4xl mx-auto text-textPrimary">
      <h2 className="text-3xl font-bold text-center text-primary mb-6">GRID Audio Tools</h2>
      <div className="grid-card rounded-lg shadow p-6">
        <LiveConversationPanel />
      </div>
      <div className="grid-card rounded-lg shadow p-6">
        <TTSPanel />
      </div>
    </div>
  );
};

export default AudioToolsPage;
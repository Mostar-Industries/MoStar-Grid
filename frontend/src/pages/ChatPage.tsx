import React, { useState } from 'react';
import axios from 'axios';

const ChatPage: React.FC = () => {
  const [input, setInput] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [contextUsed, setContextUsed] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;

    setLoading(true);
    setError('');
    setResponse('');

    try {
      const res = await axios.post('http://localhost:7000/api/chat', { 
        prompt: input 
      });
      
      setResponse(res.data.response || '[No reply]');
      setContextUsed(res.data.context_used || false);
    } catch (err: any) {
      if (err.response?.status === 503) {
        setError('⚠️ Ollama is not running. Start it with: ollama run mistral');
      } else {
        setError(`Error: ${err.response?.data?.detail || err.message}`);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && e.ctrlKey) {
      sendMessage();
    }
  };

  return (
    <div className="flex flex-col h-full p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-white flex items-center gap-3">
            <span className="text-4xl">🧠</span>
            MostarAI Chat
          </h2>
          <p className="text-gray-400 mt-1">
            Sovereign AI powered by African knowledge systems
          </p>
        </div>
        {contextUsed && (
          <div className="px-3 py-1 bg-green-900/30 border border-green-700 rounded-lg text-green-400 text-sm">
            ✓ Neo4j Context Active
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="space-y-3">
        <textarea
          rows={4}
          className="w-full p-4 border border-gray-700 rounded-lg bg-gray-800 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask about Ifá, Orisha, Gacaca, Oba Kingship, traditional medicine..."
          disabled={loading}
        />
        
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-500">
            Ctrl+Enter to send
          </span>
          <button
            className="px-6 py-2 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white font-semibold rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            onClick={sendMessage}
            disabled={loading || !input.trim()}
          >
            {loading ? (
              <>
                <i className="fas fa-spinner fa-spin"></i>
                Thinking...
              </>
            ) : (
              <>
                <i className="fas fa-paper-plane"></i>
                Ask MostarAI
              </>
            )}
          </button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="p-4 bg-red-900/30 border border-red-700 rounded-lg text-red-300">
          <i className="fas fa-exclamation-triangle mr-2"></i>
          {error}
        </div>
      )}

      {/* Response Display */}
      {response && (
        <div className="flex-1 overflow-y-auto">
          <div className="p-6 bg-gray-800 border border-gray-700 rounded-lg">
            <div className="flex items-center gap-2 mb-4 pb-3 border-b border-gray-700">
              <span className="text-2xl">🌍</span>
              <span className="text-lg font-semibold text-white">MostarAI Response</span>
            </div>
            <div className="text-gray-200 whitespace-pre-line leading-relaxed">
              {response}
            </div>
          </div>
        </div>
      )}

      {/* Empty State */}
      {!response && !loading && !error && (
        <div className="flex-1 flex items-center justify-center text-gray-500">
          <div className="text-center space-y-4">
            <div className="text-6xl">🌿</div>
            <p className="text-lg">Ask MostarAI about African wisdom traditions</p>
            <div className="text-sm space-y-1">
              <p>• "What is the Gadaa System?"</p>
              <p>• "Tell me about Ifá divination"</p>
              <p>• "What does Oba Kingship connect to?"</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatPage;

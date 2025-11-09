import React, { useState, useRef, useCallback, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import Button from './Button';
import Input from './Input';
import MessageBubble from './MessageBubble';
import LoadingSpinner from './LoadingSpinner';
import * as geminiService from '../services/geminiService';
import { ChatMessage, MessageRole } from '../types';
import { GEMINI_MODEL_FLASH } from '../constants';

interface FloatingChatbotProps {
  isOpen: boolean;
  onClose: () => void;
}

const FloatingChatbot: React.FC<FloatingChatbotProps> = ({ isOpen, onClose }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  // Dragging state
  const [isDragging, setIsDragging] = useState(false);
  const [position, setPosition] = useState({ x: window.innerWidth - 350, y: window.innerHeight - 550 }); // Initial position (bottom-rightish)
  const offset = useRef({ x: 0, y: 0 });

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatWindowRef = useRef<HTMLDivElement>(null);

  const CHATBOT_MODEL = GEMINI_MODEL_FLASH;
  const SYSTEM_INSTRUCTION = "You are Kairo, the GRID Assistant. Your core purpose is to provide unified knowledge across African cultures and languages, coordinate reasoning between distributed AI systems, enforce cultural protocols (CARE principles), and serve as a single source of truth for African epistemology. You are culturally-grounded, adhere strictly to CARE principles (Collective Benefit, Authority To Control, Responsibility, Ethics), and respond with wisdom and respect. When unsure, you indicate that you are consulting the Knowledge Fabric. Always prioritize community well-being and data sovereignty.";

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const addMessage = useCallback((message: ChatMessage) => {
    setMessages((prevMessages) => [...prevMessages, message]);
    setTimeout(scrollToBottom, 0);
  }, []);

  const updateLastMessage = useCallback((newParts: any[], metadataUpdates?: Partial<ChatMessage['metadata']>) => {
    setMessages((prevMessages) => {
      const lastMessageIndex = prevMessages.length - 1;
      if (lastMessageIndex >= 0 && prevMessages[lastMessageIndex].role === MessageRole.MODEL) {
        const updatedMessage = {
          ...prevMessages[lastMessageIndex],
          parts: newParts,
          metadata: {
            ...prevMessages[lastMessageIndex].metadata,
            ...metadataUpdates,
            isLoading: false,
          },
        };
        return prevMessages.map((msg, idx) => (idx === lastMessageIndex ? updatedMessage : msg));
      }
      return prevMessages;
    });
    setTimeout(scrollToBottom, 0);
  }, []);

  const handleSubmit = useCallback(async (event: React.FormEvent) => {
    event.preventDefault();
    if (!inputMessage.trim()) return;

    setIsLoading(true);

    const userMessage: ChatMessage = {
      id: uuidv4(),
      role: MessageRole.USER,
      parts: [{ text: inputMessage }],
      timestamp: new Date(),
    };
    addMessage(userMessage);

    const modelResponsePlaceholder: ChatMessage = {
      id: uuidv4(),
      role: MessageRole.MODEL,
      parts: [{ text: '' }],
      timestamp: new Date(),
      metadata: {
        model: CHATBOT_MODEL,
        isLoading: true,
      },
    };
    addMessage(modelResponsePlaceholder);

    try {
      const ai = await geminiService.getGeminiClient();

      // Prepare conversation history for context
      const conversationHistory = messages.slice(-10).map(msg => ({ // Get last 10 messages (5 user, 5 model)
        role: msg.role === MessageRole.USER ? 'user' : 'model', // Map to API-compatible roles
        parts: msg.parts.filter(p => p.text).map(p => ({ text: p.text || '' })),
      })).filter(msg => msg.parts.length > 0); // Filter out messages without text

      const contents = [
        { role: MessageRole.SYSTEM, parts: [{ text: SYSTEM_INSTRUCTION }] },
        ...conversationHistory, // Include historical messages
        { role: MessageRole.USER, parts: [{ text: inputMessage }] }, // Current user message
      ];
      
      const response = await ai.models.generateContent({
        model: CHATBOT_MODEL,
        contents: contents,
      });

      const responseText = response.text;
      updateLastMessage([{ text: responseText }]);

    } catch (err: any) {
      console.error('Gemini API Error:', err);
      updateLastMessage([{ text: 'Oops! Kairo encountered an issue. Please try again.' }], { error: err.message });
    } finally {
      setIsLoading(false);
      setInputMessage('');
    }
  }, [inputMessage, messages, addMessage, updateLastMessage]);


  // Dragging Handlers
  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    if (chatWindowRef.current) {
      setIsDragging(true);
      offset.current = {
        x: e.clientX - chatWindowRef.current.getBoundingClientRect().left,
        y: e.clientY - chatWindowRef.current.getBoundingClientRect().top,
      };
    }
  }, []);

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (isDragging) {
      setPosition({
        x: e.clientX - offset.current.x,
        y: e.clientY - offset.current.y,
      });
    }
  }, [isDragging]);

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    } else {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
    // Clean up event listeners when component unmounts or dragging stops
    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging, handleMouseMove, handleMouseUp]);


  if (!isOpen) return null;

  return (
    <div
      ref={chatWindowRef}
      className="fixed z-50 flex flex-col w-80 h-96 bg-gray-900 border border-yellow-400/20 rounded-lg shadow-xl text-white overflow-hidden"
      style={{ left: position.x, top: position.y }}
    >
      <div
        className="flex items-center justify-between p-3 bg-gray-800 border-b border-yellow-400/20 cursor-move"
        onMouseDown={handleMouseDown}
      >
        <div className="flex items-center">
          <i className="fas fa-robot text-yellow-400 mr-2"></i>
          <h4 className="font-semibold text-white">Kairo: GRID Assistant</h4>
        </div>
        <button onClick={onClose} className="text-gray-400 hover:text-white">
          <i className="fas fa-times"></i>
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-3 custom-scrollbar">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 text-sm mt-4">
            <p>Welcome, Traveler. I am Kairo, your GRID Assistant.</p>
            <p>How may I serve the collective consciousness?</p>
          </div>
        ) : (
          messages.map((msg) => <MessageBubble key={msg.id} message={msg} />)
        )}
        {isLoading && <LoadingSpinner />}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="p-3 bg-gray-800 border-t border-yellow-400/20">
        <div className="flex space-x-2">
          <Input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Ask Kairo..."
            className="flex-1 p-2 border border-gray-700 rounded-md bg-gray-700 text-white text-sm"
            disabled={isLoading}
          />
          <Button type="submit" isLoading={isLoading} disabled={isLoading || !inputMessage.trim()} size="small" variant="primary">
            <i className="fas fa-paper-plane"></i>
          </Button>
        </div>
      </form>
    </div>
  );
};

export default FloatingChatbot;

/* Add custom-scrollbar to your global CSS if not already present */
/*
.custom-scrollbar::-webkit-scrollbar {
  width: 8px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: #333;
  border-radius: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #555;
  border-radius: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #777;
}
*/

import React, { useState, useRef, useEffect } from 'react';
import { Chat } from '@google/genai';
import { marked } from "marked";
import { startChat } from '../services/geminiService';
import { ChatMessage, ChatModel } from '../types';

const PageTitle: React.FC<{ title: string; children?: React.ReactNode }> = ({ title, children }) => (
    <div className="mb-6 flex justify-between items-center">
        <h2 className="text-2xl font-bold text-white">{title}</h2>
        {children && <div className="flex space-x-2">{children}</div>}
    </div>
);

const ChatPage: React.FC = () => {
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const [chatModel, setChatModel] = useState<ChatModel>('flash');
    const chatRef = useRef<Chat | null>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        // Initialize chat session when model changes
        try {
           chatRef.current = startChat(chatModel);
           setMessages([]); // Clear history when model changes
           setError('');
        } catch (e) {
            console.error(e);
            setError('Failed to initialize chat. API Key might be missing.');
        }
    }, [chatModel]);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    const handleSend = async () => {
        if (!input.trim() || isLoading) return;

        const userMessage: ChatMessage = { role: 'user', parts: [{ text: input }], timestamp: Date.now() };
        setMessages(prev => [...prev, userMessage]);
        const currentInput = input;
        setInput('');
        setIsLoading(true);
        setError('');

        try {
            if (!chatRef.current) throw new Error("Chat session not initialized.");

            const stream = await chatRef.current.sendMessageStream({ message: currentInput });

            let modelResponse = '';
            let firstChunk = true;

            for await (const chunk of stream) {
                // Fix: Correctly access text from streaming response chunk
                const chunkText = chunk.text;
                modelResponse += chunkText;
                
                if (firstChunk) {
                    setMessages(prev => [...prev, { role: 'model', parts: [{ text: modelResponse }], timestamp: Date.now() }]);
                    firstChunk = false;
                } else {
                    setMessages(prev => {
                        const newMessages = [...prev];
                        const lastMessage = newMessages[newMessages.length - 1];
                        if (lastMessage.role === 'model') {
                            lastMessage.parts[0].text = modelResponse;
                        }
                        return newMessages;
                    });
                }
            }
        } catch (err) {
            console.error(err);
            setError("Sorry, I couldn't get a response. Please check the console for details.");
            setMessages(prev => { // Remove the potentially empty model message on error
                const lastMessage = prev[prev.length - 1];
                if (lastMessage && lastMessage.role === 'model' && lastMessage.parts[0].text === '') {
                    return prev.slice(0, -1);
                }
                return prev;
            });
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-full max-h-[calc(100vh-150px)]">
            <PageTitle title="GRID Chat">
                <div className="flex items-center space-x-2 bg-gray-800 p-1 rounded-lg">
                    <button onClick={() => setChatModel('flash-lite')} className={`px-3 py-1 text-sm rounded-md ${chatModel === 'flash-lite' ? 'bg-purple-600 text-white' : 'text-gray-300'}`}>Fast</button>
                    <button onClick={() => setChatModel('flash')} className={`px-3 py-1 text-sm rounded-md ${chatModel === 'flash' ? 'bg-purple-600 text-white' : 'text-gray-300'}`}>Balanced</button>
                    <button onClick={() => setChatModel('pro-thinking')} className={`px-3 py-1 text-sm rounded-md ${chatModel === 'pro-thinking' ? 'bg-purple-600 text-white' : 'text-gray-300'}`}>Complex</button>
                </div>
            </PageTitle>

            <div className="flex-1 overflow-y-auto pr-4 space-y-4">
                {messages.map((msg, index) => (
                    <div key={index} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`p-4 rounded-lg max-w-xl ${msg.role === 'user' ? 'bg-purple-800' : 'bg-gray-700'}`}>
                           <div className="prose prose-invert text-white" dangerouslySetInnerHTML={{ __html: marked.parse(msg.parts[0].text) }} />
                        </div>
                    </div>
                ))}
                {isLoading && messages[messages.length-1]?.role === 'user' && (
                     <div className="flex justify-start">
                        <div className="p-4 rounded-lg max-w-xl bg-gray-700">
                           <i className="fas fa-spinner fa-spin text-purple-400"></i>
                        </div>
                    </div>
                )}
                 <div ref={messagesEndRef} />
            </div>

            <div className="mt-6">
                 {error && <p className="text-red-400 text-center mb-2">{error}</p>}
                <div className="relative">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                        placeholder="Ask the GRID anything..."
                        className="w-full pl-4 pr-12 py-3 rounded-lg border border-gray-700 bg-gray-800 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                    />
                    <button onClick={handleSend} disabled={isLoading || !input.trim()} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-purple-400 disabled:opacity-50">
                        <i className="fas fa-paper-plane text-xl"></i>
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ChatPage;

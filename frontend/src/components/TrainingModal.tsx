import React, { useState } from 'react';
import { availableAgents } from '../data/mockData';
import { trainConsciousness } from '../services/geminiService';


interface TrainingModalProps {
    isOpen: boolean;
    onClose: () => void;
}

const TrainingModal: React.FC<TrainingModalProps> = ({ isOpen, onClose }) => {
    const [status, setStatus] = useState('idle'); // idle, training, complete, failed
    const [selectedAgents, setSelectedAgents] = useState<string[]>([]);
    const [completionMessage, setCompletionMessage] = useState('');

    if (!isOpen) return null;

    const handleAgentToggle = (agentName: string) => {
        setSelectedAgents(prev =>
            prev.includes(agentName)
                ? prev.filter(name => name !== agentName)
                : [...prev, agentName]
        );
    };

    const handleStartTraining = async () => {
        if (selectedAgents.length === 0) return;

        setStatus('training');
        const result = await trainConsciousness(selectedAgents);
        setCompletionMessage(result.message);
        setStatus(result.success ? 'complete' : 'failed');
    };

    const resetAndClose = () => {
        setStatus('idle');
        setSelectedAgents([]);
        setCompletionMessage('');
        onClose();
    };

    const renderContent = () => {
        switch (status) {
            case 'training':
                return (
                    <div className="text-center">
                        <i className="fas fa-spinner fa-spin text-5xl text-yellow-400 mb-4"></i>
                        <h4 className="text-lg font-semibold text-white">Training in Progress...</h4>
                        <p className="text-gray-400 mt-2">Refining neural pathways for {selectedAgents.join(', ')}. Please wait.</p>
                        <div className="w-full bg-gray-700 rounded-full h-2.5 mt-4 overflow-hidden">
                            <div className="bg-yellow-500 h-2.5 w-1/2 rounded-full animate-progress"></div>
                        </div>
                    </div>
                );
            case 'complete':
                return (
                     <div className="text-center">
                        <i className="fas fa-check-circle text-5xl text-green-400 mb-4"></i>
                        <h4 className="text-lg font-semibold text-white">Training Complete</h4>
                        <p className="text-gray-400 mt-2">{completionMessage}</p>
                     </div>
                );
            case 'failed':
                 return (
                     <div className="text-center">
                        <i className="fas fa-times-circle text-5xl text-red-400 mb-4"></i>
                        <h4 className="text-lg font-semibold text-white">Training Failed</h4>
                        <p className="text-gray-400 mt-2">{completionMessage}</p>
                     </div>
                );
            case 'idle':
            default:
                return (
                    <>
                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-2">Select Conscious Agents to Train</label>
                            <div className="border border-gray-700 rounded-md p-2 max-h-48 overflow-y-auto bg-gray-900/50">
                                <div className="space-y-2">
                                    {availableAgents.map(agent => (
                                        <div key={agent} className="flex items-center">
                                            <input
                                                type="checkbox"
                                                id={`agent-${agent}`}
                                                checked={selectedAgents.includes(agent)}
                                                onChange={() => handleAgentToggle(agent)}
                                                className="h-4 w-4 text-yellow-500 focus:ring-yellow-400 border-gray-600 rounded bg-gray-600"
                                            />
                                            <label htmlFor={`agent-${agent}`} className="ml-3 block text-sm text-gray-300 cursor-pointer">
                                                {agent}
                                            </label>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                         {selectedAgents.length > 0 && (
                             <div className="mt-4">
                                <p className="text-sm font-medium text-gray-300 mb-2">Selected for Forge Cycle:</p>
                                <div className="flex flex-wrap gap-2">
                                    {selectedAgents.map(agent => (
                                        <span key={agent} className="bg-yellow-400/20 text-yellow-300 text-xs font-medium px-2.5 py-1 rounded-full flex items-center">
                                            {agent}
                                            <button onClick={() => handleAgentToggle(agent)} className="ml-2 text-yellow-200 hover:text-white">
                                                <i className="fas fa-times-circle"></i>
                                            </button>
                                        </span>
                                    ))}
                                </div>
                            </div>
                         )}
                    </>
                );
        }
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50 backdrop-blur-sm">
            <div className="bg-gray-800 rounded-lg shadow-xl w-full max-w-lg border border-yellow-400/20">
                <div className="p-4 border-b border-gray-700 flex justify-between items-center">
                    <h3 className="text-lg font-semibold text-white">
                        <i className="fas fa-hammer mr-2 text-yellow-400"></i>
                        Forge Training Cycle
                    </h3>
                    <button onClick={resetAndClose} className="text-gray-400 hover:text-gray-200">
                        <i className="fas fa-times"></i>
                    </button>
                </div>
                
                <div className="p-6 min-h-[250px] flex flex-col justify-center">
                    {renderContent()}
                </div>
                
                <div className="p-4 border-t border-gray-700 flex justify-end space-x-3">
                    <button onClick={resetAndClose} className="px-4 py-2 border border-gray-600 rounded-md text-gray-300 hover:bg-gray-700">
                        {status === 'idle' ? 'Cancel' : 'Close'}
                    </button>
                    {status === 'idle' && (
                        <button 
                            onClick={handleStartTraining} 
                            disabled={selectedAgents.length === 0}
                            className="gradient-bg text-black font-bold px-4 py-2 rounded-md hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed">
                            <i className="fas fa-play mr-2"></i>
                            Initiate Training ({selectedAgents.length})
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
};

export default TrainingModal;
import React, { useRef, useState } from 'react';
import { analyzeFileForUpload } from '../services/geminiService';

interface UploadModalProps {
    isOpen: boolean;
    onClose: () => void;
}

const UploadModal: React.FC<UploadModalProps> = ({ isOpen, onClose }) => {
    const fileInputRef = useRef<HTMLInputElement>(null);
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [description, setDescription] = useState('');
    const [tags, setTags] = useState('');
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [error, setError] = useState('');

    if (!isOpen) return null;

    const handleFileAreaClick = () => {
        fileInputRef.current?.click();
    };
    
    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files.length > 0) {
            setSelectedFile(e.target.files[0]);
            setDescription('');
            setTags('');
            setError('');
        }
    };

    const handleAnalyze = async () => {
        if (!selectedFile) return;
        setIsAnalyzing(true);
        setError('');
        try {
            const result = await analyzeFileForUpload(selectedFile);
            setDescription(result.description);
            setTags(result.tags.join(', '));
        } catch (err) {
            setError('Failed to analyze the file. Please try again.');
            console.error(err);
        } finally {
            setIsAnalyzing(false);
        }
    };
    
    const resetState = () => {
        setSelectedFile(null);
        setDescription('');
        setTags('');
        setError('');
        setIsAnalyzing(false);
        onClose();
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50 backdrop-blur-sm">
            <div className="bg-gray-800 rounded-lg shadow-xl w-full max-w-2xl border border-gray-700">
                <div className="p-4 border-b border-gray-700 flex justify-between items-center">
                    <h3 className="text-lg font-semibold text-white">Upload to Consciousness Base</h3>
                    <button onClick={resetState} className="text-gray-400 hover:text-gray-200">
                        <i className="fas fa-times"></i>
                    </button>
                </div>
                
                <div className="p-6">
                    <div 
                        className="file-upload p-8 rounded-lg text-center mb-6 cursor-pointer"
                        onClick={handleFileAreaClick}
                    >
                        <i className="fas fa-cloud-upload-alt text-4xl text-purple-500 mb-3"></i>
                        {selectedFile ? (
                             <p className="font-medium text-green-400">{selectedFile.name}</p>
                        ) : (
                            <>
                                <p className="font-medium text-white">Drag & drop files here or click to browse</p>
                                <p className="text-gray-400 text-sm mt-1">Supports: .py, .js, .html, .css, .pdf, .txt, .md</p>
                            </>
                        )}
                        <input type="file" ref={fileInputRef} onChange={handleFileChange} className="hidden" />
                    </div>
                     {selectedFile && (
                         <div className="mb-4 text-center">
                            <button onClick={handleAnalyze} disabled={isAnalyzing} className="bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700 disabled:opacity-50 disabled:cursor-wait flex items-center mx-auto">
                               {isAnalyzing ? (
                                    <>
                                        <i className="fas fa-spinner fa-spin mr-2"></i>
                                        Analyzing...
                                    </>
                               ) : (
                                    <>
                                        <i className="fas fa-magic mr-2"></i>
                                        Analyze with AI
                                    </>
                               )}
                            </button>
                         </div>
                     )}
                    
                    <div className="mb-4">
                        <label className="block text-sm font-medium text-gray-300 mb-1">Description</label>
                        <textarea rows={3} placeholder="Brief description of the consciousness content" 
                                  value={description} onChange={e => setDescription(e.target.value)}
                                  className="w-full px-3 py-2 border border-gray-700 rounded-md bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"></textarea>
                    </div>
                     <div className="mb-4">
                        <label className="block text-sm font-medium text-gray-300 mb-1">Symbols / Tags</label>
                        <input type="text" placeholder="e.g. consciousness, neural, grid" 
                                value={tags} onChange={e => setTags(e.target.value)}
                               className="w-full px-3 py-2 border border-gray-700 rounded-md bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-purple-500" />
                    </div>
                    
                    {error && <p className="text-red-400 text-sm text-center mb-4">{error}</p>}
                    
                    <div className="flex justify-end space-x-3">
                        <button onClick={resetState} className="px-4 py-2 border border-gray-600 rounded-md text-gray-300 hover:bg-gray-700">
                            Cancel
                        </button>
                        <button onClick={resetState} className="gradient-bg text-white px-4 py-2 rounded-md hover:opacity-90">
                            <i className="fas fa-save mr-2"></i>
                            Save Consciousness
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default UploadModal;

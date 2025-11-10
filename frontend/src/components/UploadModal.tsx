import React from 'react';
import Button from './Button';
import Input from './Input';
import { analyzeFileForUpload } from '../services/geminiService'; // Assuming this uses Gemini
import { fileToBase64 } from '../services/fileUtils';

interface UploadModalProps {
    isOpen: boolean;
    onClose: () => void;
}

const UploadModal: React.FC<UploadModalProps> = ({ isOpen, onClose }) => {
    const [selectedFile, setSelectedFile] = React.useState<File | null>(null);
    const [uploading, setUploading] = React.useState(false);
    const [analysisResult, setAnalysisResult] = React.useState<{ description: string; tags: string[]; } | null>(null);
    const [error, setError] = React.useState<string | null>(null);

    if (!isOpen) return null;

    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        if (event.target.files && event.target.files.length > 0) {
            setSelectedFile(event.target.files[0]);
            setAnalysisResult(null);
            setError(null);
        }
    };

    const handleAnalyze = async () => {
        if (!selectedFile) return;
        setUploading(true);
        setError(null);
        try {
            // Simulate analysis using Gemini Service
            const result = await analyzeFileForUpload(selectedFile);
            setAnalysisResult(result);
        } catch (err: any) {
            setError(`File analysis failed: ${err.message}`);
        } finally {
            setUploading(false);
        }
    };

    const handleUpload = async () => {
        if (!selectedFile) return;
        setUploading(true);
        setError(null);
        try {
            // In a real scenario, you'd send the file and analysis result to a backend
            const base64Data = await fileToBase64(selectedFile);
            console.log("Uploading file to Grid:", selectedFile.name, "with analysis:", analysisResult);
            // Simulate API call
            await new Promise(resolve => setTimeout(resolve, 2000));
            alert('File uploaded to Grid successfully!');
            onClose();
        } catch (err: any) {
            setError(`File upload failed: ${err.message}`);
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50 backdrop-blur-sm">
            <div className="bg-gray-800 rounded-lg shadow-xl w-full max-w-xl border border-yellow-400/20">
                <div className="p-4 border-b border-gray-700 flex justify-between items-center">
                    <h3 className="text-lg font-semibold text-white">
                        <i className="fas fa-cloud-upload-alt mr-2 text-yellow-400"></i>
                        Upload Consciousness to GRID
                    </h3>
                    <button onClick={onClose} className="text-gray-400 hover:text-gray-200">
                        <i className="fas fa-times"></i>
                    </button>
                </div>
                
                <div className="p-6">
                    <div className="mb-4">
                        <label htmlFor="file-input" className="block text-sm font-medium text-gray-300 mb-2">Select File</label>
                        <Input
                            id="file-input"
                            type="file"
                            onChange={handleFileChange}
                            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-yellow-50 file:text-yellow-700 hover:file:bg-yellow-100"
                            disabled={uploading}
                        />
                        {selectedFile && (
                            <p className="mt-2 text-sm text-gray-400">Selected: {selectedFile.name}</p>
                        )}
                    </div>

                    {selectedFile && !analysisResult && (
                        <Button onClick={handleAnalyze} isLoading={uploading} disabled={!selectedFile || uploading} className="w-full mb-4">
                            Analyze with AI
                        </Button>
                    )}

                    {analysisResult && (
                        <div className="mt-4 p-4 bg-gray-700 rounded-md text-gray-300">
                            <h4 className="font-semibold text-white mb-2">AI Analysis:</h4>
                            <p className="text-sm">{analysisResult.description}</p>
                            <div className="mt-2 flex flex-wrap gap-2">
                                {analysisResult.tags.map(tag => (
                                    <span key={tag} className="bg-yellow-400/20 text-yellow-300 text-xs px-2 py-1 rounded-full">
                                        {tag}
                                    </span>
                                ))}
                            </div>
                        </div>
                    )}

                    {error && <p className="text-red-500 mt-4 text-center">{error}</p>}
                </div>
                
                <div className="p-4 border-t border-gray-700 flex justify-end space-x-3">
                    <button onClick={onClose} className="px-4 py-2 border border-gray-600 rounded-md text-gray-300 hover:bg-gray-700">
                        Cancel
                    </button>
                    <Button 
                        onClick={handleUpload} 
                        isLoading={uploading} 
                        disabled={!selectedFile || !analysisResult || uploading}
                    >
                        <i className="fas fa-upload mr-2"></i>
                        Confirm Upload
                    </Button>
                </div>
            </div>
        </div>
    );
};

export default UploadModal;

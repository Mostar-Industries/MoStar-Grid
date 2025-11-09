import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { analyzeImage, analyzeVideo } from '../services/geminiService';

const PageTitle: React.FC<{ title: string; children?: React.ReactNode }> = ({ title, children }) => (
    <div className="mb-6 flex justify-between items-center">
        <h2 className="text-2xl font-bold text-white">{title}</h2>
        {children && <div className="flex space-x-2">{children}</div>}
    </div>
);

interface VisionPageProps {
    isSentinelMode: boolean;
}

const VisionPage: React.FC<VisionPageProps> = ({ isSentinelMode }) => {
    const [file, setFile] = useState<File | null>(null);
    const [preview, setPreview] = useState<string | null>(null);
    const [prompt, setPrompt] = useState('Describe this content in detail.');
    const [isLoading, setIsLoading] = useState(false);
    const [result, setResult] = useState('');
    const [error, setError] = useState('');

    const onDrop = useCallback((acceptedFiles: File[]) => {
        if (acceptedFiles.length > 0) {
            const currentFile = acceptedFiles[0];
            setFile(currentFile);
            setResult('');
            setError('');
            if (currentFile.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onloadend = () => {
                    setPreview(reader.result as string);
                };
                reader.readAsDataURL(currentFile);
            } else {
                 setPreview(null); // No preview for video
            }
        }
    }, []);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: { 'image/*': ['.jpeg', '.png', '.gif', '.webp'], 'video/*': ['.mp4', '.mov', '.webm'] },
        multiple: false,
        disabled: isSentinelMode
    });

    const handleAnalyze = async () => {
        if (!file) return;
        setIsLoading(true);
        setError('');
        setResult('');

        try {
            let analysisResult = '';
            if (file.type.startsWith('image/')) {
                analysisResult = await analyzeImage(prompt, file);
            } else if (file.type.startsWith('video/')) {
                analysisResult = await analyzeVideo(prompt, file);
            }
            setResult(analysisResult);
        } catch (err) {
            console.error(err);
            setError('Failed to analyze the file. The API key might be missing or invalid.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div>
            <PageTitle title="Vision Analysis" />
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                    <div {...getRootProps()} className={`file-upload p-8 rounded-lg text-center h-64 flex flex-col items-center justify-center ${isSentinelMode ? 'cursor-not-allowed bg-gray-800/50' : 'cursor-pointer'} ${isDragActive ? 'bg-purple-500/20' : ''}`}>
                        <input {...getInputProps()} />
                        {isSentinelMode ? (
                            <>
                                <i className="fas fa-lock text-4xl text-cyan-400 mb-3"></i>
                                <p className="font-medium text-cyan-400">Vision Analysis Sealed</p>
                            </>
                        ) : (
                            <>
                                <i className="fas fa-eye text-4xl text-purple-500 mb-3"></i>
                                {file ? (
                                    <p className="font-medium text-green-400">{file.name}</p>
                                ) : (
                                    isDragActive ?
                                        <p>Drop the file here ...</p> :
                                        <p>Drag & drop an image or video here, or click to select</p>
                                )}
                            </>
                        )}
                    </div>

                    {preview && !isSentinelMode && (
                        <div className="mt-4 p-2 border border-gray-700 rounded-lg">
                            <img src={preview} alt="Preview" className="max-h-64 w-auto mx-auto rounded" />
                        </div>
                    )}

                    <div className="mt-4">
                        <label className="block text-sm font-medium text-gray-300 mb-1">Analysis Prompt</label>
                        <textarea
                            value={prompt}
                            onChange={e => setPrompt(e.target.value)}
                            rows={3}
                            disabled={isSentinelMode}
                            className="w-full px-3 py-2 border border-gray-700 rounded-md bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:bg-gray-800"
                        />
                    </div>
                    <button onClick={handleAnalyze} disabled={!file || isLoading || isSentinelMode} className="gradient-bg w-full mt-4 text-white px-4 py-3 rounded-md hover:opacity-90 flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed">
                       {isLoading ? (
                           <>
                               <i className="fas fa-spinner fa-spin mr-2"></i>
                               Analyzing...
                           </>
                       ) : (
                           <>
                                <i className="fas fa-microchip mr-2"></i>
                                Analyze Content
                           </>
                       )}
                    </button>
                </div>
                <div>
                    <h3 className="text-lg font-bold text-white mb-2">Analysis Result</h3>
                    <div className="bg-gray-800 border border-gray-700 rounded-lg p-4 min-h-[400px]">
                        {isLoading && <p className="text-purple-400">Analysis in progress...</p>}
                        {error && <p className="text-red-400">{error}</p>}
                        {result && <p className="text-gray-300 whitespace-pre-wrap">{result}</p>}
                         {!isLoading && !error && !result && <p className="text-gray-500">Upload a file and click Analyze to see the result here.</p>}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default VisionPage;
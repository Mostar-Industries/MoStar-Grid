import React, { useState } from 'react';
import { generateImageFromText } from '../services/geminiService'; // FIX: Corrected import path for generateImageFromText

const PageTitle: React.FC<{ title: string; children?: React.ReactNode }> = ({ title, children }) => (
    <div className="mb-6 flex justify-between items-center">
        <h2 className="text-2xl font-bold text-white">{title}</h2>
        {children && <div className="flex space-x-2">{children}</div>}
    </div>
);

const ImageForgePage: React.FC = () => {
    const [prompt, setPrompt] = useState('A quantum computer core, glowing with intricate blue and gold energy, floating in a dark, minimalist chamber.');
    const [numImages, setNumImages] = useState(1);
    const [imageSize, setImageSize] = useState('1024x1024');
    const [isLoading, setIsLoading] = useState(false);
    const [images, setImages] = useState<string[]>([]);
    const [error, setError] = useState('');

    const handleGenerate = async () => {
        if (!prompt) return;
        setIsLoading(true);
        setError('');
        setImages([]);

        try {
            const generatedImages = await generateImageFromText(prompt, numImages, imageSize);
            setImages(generatedImages);
        } catch (err) {
            console.error(err);
            const errorMessage = err instanceof Error ? err.message : 'An unknown error occurred.';
            setError(`Failed to generate images. Please check your API key and network connection. Error: ${errorMessage}`);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div>
            <PageTitle title="Image Forge" />
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Controls Column */}
                <div className="grid-card p-6 rounded-lg">
                    <div className="mb-4">
                        <label className="block text-sm font-medium text-gray-300 mb-2">Prompt</label>
                        <textarea
                            value={prompt}
                            onChange={(e) => setPrompt(e.target.value)}
                            rows={6}
                            placeholder="Enter a detailed description of the image to generate..."
                            className="w-full px-3 py-2 border border-gray-700 rounded-md bg-gray-800 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                        />
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4 mb-6">
                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-2">Number of Images</label>
                            <select
                                value={numImages}
                                onChange={(e) => setNumImages(parseInt(e.target.value))}
                                className="w-full px-3 py-2 border border-gray-700 rounded-md bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                            >
                                <option value={1}>1</option>
                                <option value={2}>2</option>
                                <option value={3}>3</option>
                                <option value={4}>4</option>
                            </select>
                        </div>
                        <div>
                             <label className="block text-sm font-medium text-gray-300 mb-2">Size</label>
                            <select
                                value={imageSize}
                                onChange={(e) => setImageSize(e.target.value)}
                                className="w-full px-3 py-2 border border-gray-700 rounded-md bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                            >
                                <option value="1024x1024">1024x1024</option>
                                <option value="512x512">512x512</option>
                                <option value="256x256">256x256</option>
                            </select>
                        </div>
                    </div>

                    <button
                        onClick={handleGenerate}
                        disabled={isLoading}
                        className="gradient-bg w-full text-white px-4 py-3 rounded-md hover:opacity-90 flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {isLoading ? (
                            <>
                                <i className="fas fa-spinner fa-spin mr-2"></i>
                                Forging Images...
                            </>
                        ) : (
                            <>
                                <i className="fas fa-magic mr-2"></i>
                                Generate
                            </>
                        )}
                    </button>
                </div>

                {/* Results Column */}
                <div>
                    <h3 className="text-lg font-bold text-white mb-2">Generated Images</h3>
                    <div className="bg-gray-800 border border-gray-700 rounded-lg p-4 min-h-[450px] flex items-center justify-center">
                        {isLoading && <div className="text-center text-purple-400"><i className="fas fa-spinner fa-spin text-4xl mb-4"></i><p>The AI is forging your vision...</p></div>}
                        {error && <p className="text-red-400 text-center whitespace-pre-wrap">{error}</p>}
                        {!isLoading && !error && images.length === 0 && (
                            <div className="text-center text-gray-500">
                                <i className="fas fa-image text-5xl mb-4"></i>
                                <p>Generated images will appear here.</p>
                            </div>
                        )}
                        {images.length > 0 && (
                            <div className={`grid grid-cols-1 ${images.length > 1 ? 'md:grid-cols-2' : ''} gap-4 w-full`}>
                                {images.map((imgSrc, index) => (
                                    <div key={index} className="rounded-lg overflow-hidden border-2 border-purple-800/50">
                                        <img src={imgSrc} alt={`Generated image ${index + 1}`} className="w-full h-full object-cover"/>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ImageForgePage;
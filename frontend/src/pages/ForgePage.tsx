
import React, { useState } from 'react';
import { marked } from "marked";

const PageTitle: React.FC<{ title: string; children?: React.ReactNode }> = ({ title, children }) => (
    <div className="mb-6 flex justify-between items-center">
        <h2 className="text-2xl font-bold text-white">{title}</h2>
        {children && <div className="flex space-x-2">{children}</div>}
    </div>
);

const ForgePage: React.FC = () => {
    const [prompt, setPrompt] = useState('Write a python script to visualize real-time stock market data from an API.');
    const [isLoading, setIsLoading] = useState(false);
    const [result, setResult] = useState('');
    const [error, setError] = useState('');

    const handleForge = async () => {
        if (!prompt) return;
        setIsLoading(true);
        setError('');
        setResult('');

        try {
            // Call backend API for content generation
            const response = await fetch('/api/forge', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt })
            });
            
            if (!response.ok) throw new Error('API request failed');
            
            const data = await response.json();
            setResult(data.result || 'Content generated successfully');

        } catch (err) {
            console.error(err);
            const errorMessage = err instanceof Error ? err.message : 'An unknown error occurred.';
            setError(`Failed to generate content. Please check your API key and network connection. Error: ${errorMessage}`);
        } finally {
            setIsLoading(false);
        }
    };


    return (
        <div>
            <PageTitle title="The Forge">
                 <p className="text-sm text-gray-400">Advanced creation and synthesis powered by Gemini 2.5 Pro.</p>
            </PageTitle>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                     <div className="mb-4">
                        <label className="block text-sm font-medium text-gray-300 mb-1">Synthesis Prompt</label>
                        <textarea
                            value={prompt}
                            onChange={e => setPrompt(e.target.value)}
                            rows={10}
                            placeholder="Enter a complex prompt for code generation, analysis, or creative writing..."
                            className="w-full px-3 py-2 border border-gray-700 rounded-md bg-gray-800 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                        />
                    </div>
                     <button onClick={handleForge} disabled={isLoading} className="gradient-bg w-full mt-2 text-white px-4 py-3 rounded-md hover:opacity-90 flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed">
                       {isLoading ? (
                           <>
                               <i className="fas fa-spinner fa-spin mr-2"></i>
                               Synthesizing...
                           </>
                       ) : (
                           <>
                                <i className="fas fa-hammer mr-2"></i>
                                Forge Content
                           </>
                       )}
                    </button>
                </div>
                <div>
                    <h3 className="text-lg font-bold text-white mb-2">Generated Output</h3>
                    <div className="bg-gray-800 border border-gray-700 rounded-lg p-4 min-h-[400px] max-h-[60vh] overflow-y-auto">
                        {isLoading && <p className="text-purple-400">The Forge is running...</p>}
                        {error && <p className="text-red-400 whitespace-pre-wrap">{error}</p>}
                        {result && (
                            <div 
                                className="prose prose-invert text-white max-w-none" 
                                dangerouslySetInnerHTML={{ __html: marked.parse(result) }} 
                            />
                        )}
                         {!isLoading && !error && !result && <p className="text-gray-500">The output of your synthesis will appear here.</p>}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ForgePage;

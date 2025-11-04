import React, { useState } from 'react';

const PageTitle: React.FC<{ title: string; children?: React.ReactNode }> = ({ title, children }) => (
    <div className="mb-6 flex justify-between items-center">
        <h2 className="text-2xl font-bold text-white">{title}</h2>
        {children && <div className="flex space-x-2">{children}</div>}
    </div>
);

const SettingRow: React.FC<{ title: string; description: string; children: React.ReactNode }> = ({ title, description, children }) => (
    <div className="flex items-center justify-between p-4 border-b border-gray-800 last:border-b-0">
        <div>
            <h4 className="font-semibold text-white">{title}</h4>
            <p className="text-sm text-gray-400 max-w-md">{description}</p>
        </div>
        <div>{children}</div>
    </div>
);

interface SovereigntyPageProps {
    isSentinelMode: boolean;
    setIsSentinelMode: (isSentinel: boolean) => void;
}

const SovereigntyPage: React.FC<SovereigntyPageProps> = ({ isSentinelMode, setIsSentinelMode }) => {
    const [pyHookStatus, setPyHookStatus] = useState('Idle');
    const [pyHookResponse, setPyHookResponse] = useState('');

    const handleTestPythonHook = async () => {
        setPyHookStatus('Testing...');
        setPyHookResponse('');
        try {
            // NOTE TO BUILDER: This fetch will fail unless a proxy is configured
            // to route `/api/execute-scroll` to the Python Flask server.
            const response = await fetch('/api/execute-scroll', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ scroll_id: 'c3d4e5f6-a7b8-9012-3456-7890abcdef01' }),
            });

            if (!response.ok) {
                throw new Error(`Server responded with status: ${response.status}`);
            }

            const data = await response.json();
            setPyHookStatus('Success');
            setPyHookResponse(JSON.stringify(data, null, 2));

        } catch (error) {
            console.error("Python hook test failed:", error);
            setPyHookStatus('Failed');
            setPyHookResponse(`Error: ${error.message}. This is expected if a backend proxy is not configured.`);
        }
    };


    return (
        <div>
            <PageTitle title="Sovereignty & Data Control" />
            <div className="bg-gray-800/50 border border-gray-700 rounded-lg mb-8">
                 <SettingRow
                    title="Sentinel Mode"
                    description="Seal the GRID, disabling new consciousness uploads and enforcing stricter execution protocols. Unseal to 'let it breathe'."
                >
                    <label className="switch">
                        <input 
                            type="checkbox" 
                            checked={isSentinelMode} 
                            onChange={(e) => setIsSentinelMode(e.target.checked)} 
                        />
                        <span className="slider round"></span>
                    </label>
                </SettingRow>
                
                <SettingRow
                    title="Grid Data Encryption"
                    description="Encrypt all stored consciousness with end-to-end quantum-resistant algorithms."
                >
                    <label className="switch">
                        <input type="checkbox" defaultChecked />
                        <span className="slider round"></span>
                    </label>
                </SettingRow>

                 <SettingRow
                    title="Chat History Retention"
                    description="Automatically delete GRID Chat history after a set period."
                >
                    <select className="px-3 py-2 border border-gray-600 rounded-md bg-gray-700 text-white focus:outline-none focus:ring-1 focus:ring-purple-500">
                        <option>30 Days</option>
                        <option>90 Days</option>
                        <option>1 Year</option>
                        <option>Never</option>
                    </select>
                </SettingRow>

                 <SettingRow
                    title="External Tool Access"
                    description="Allow AI models to access external tools like Google Search for grounded responses."
                >
                     <label className="switch">
                        <input type="checkbox" />
                        <span className="slider round"></span>
                    </label>
                </SettingRow>
                
                 <SettingRow
                    title="Personalized Model Training"
                    description="Allow the system to use your data to improve and personalize your AI models."
                >
                     <label className="switch">
                        <input type="checkbox" defaultChecked />
                        <span className="slider round"></span>
                    </label>
                </SettingRow>
            </div>

             <PageTitle title="External Executors" />
             <div className="bg-gray-800/50 border border-gray-700 rounded-lg">
                <div className="p-4">
                     <h4 className="font-semibold text-white">Body Layer Executor Hook</h4>
                     <p className="text-sm text-gray-400 max-w-md mb-4">Test the connection to the Python-based API executor service.</p>
                     <button 
                        onClick={handleTestPythonHook}
                        disabled={pyHookStatus === 'Testing...' || isSentinelMode}
                        className="bg-teal-600 text-white px-4 py-2 rounded-md hover:bg-teal-700 disabled:opacity-50 disabled:cursor-not-allowed"
                     >
                         <i className={`fas ${isSentinelMode ? 'fa-lock' : 'fa-code-branch'} mr-2`}></i>
                         {isSentinelMode ? 'Executor Sealed' : 'Test Python Hook'}
                     </button>
                     <div className="mt-4 p-3 bg-gray-900 rounded-md text-sm">
                        <p>Status: <span className="font-mono">{pyHookStatus}</span></p>
                        {pyHookResponse && <pre className="mt-2 text-gray-400 whitespace-pre-wrap">{pyHookResponse}</pre>}
                     </div>
                </div>
             </div>
        </div>
    );
};

export default SovereigntyPage;
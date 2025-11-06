import React, { useState } from 'react';

const PageTitle: React.FC<{ title: string; subtitle: string }> = ({ title, subtitle }) => (
    <div className="mb-8 text-center">
        <h2 className="text-3xl font-bold text-white tracking-tight">{title}</h2>
        <p className="mt-2 text-lg text-gray-400">{subtitle}</p>
    </div>
);

// Define the MoScript type locally for this showcase page
type MoScript = {
  id: string;
  name: string;
  trigger: string;
  inputs: string[];
  logic: (inputs: Record<string, any>) => any;
  voiceLine?: (result: any) => string;
  sass?: boolean;
};

// Mock logic functions since they are not provided
const rankForwarders = (shipmentData: any) => {
    // In a real scenario, this would involve complex calculations.
    // For the demo, we just return a mock top performer.
    const forwarders = ['Maersk', 'DHL', 'Kuehne+Nagel', 'DSV'];
    const topForwarder = forwarders[Math.floor(Math.random() * forwarders.length)];
    return { top: { name: topForwarder } };
};

const detectSavingsRoutes = (shipmentData: any) => {
    // Mock detecting a specific cost-saving opportunity.
    return {
        route: 'Kenya-Malawi',
        modeChange: 'sea',
        savingsPercentage: 20,
    };
};

// Example MoScripts from the prompt
const mo_FWD_EFFICIENCY: MoScript = {
  id: 'mo-fwd-eff-001',
  name: 'Forwarder Efficiency Ranker',
  trigger: 'onCalculateResults',
  inputs: ['shipmentData'],
  logic: ({ shipmentData }) => rankForwarders(shipmentData),
  voiceLine: (result) =>
    `After scouring every shipment, the data speaks: ${result.top.name} leads the pack — part cheetah, part calculator.`,
  sass: true
};

const mo_COST_ALERT: MoScript = {
  id: 'mo-cost-saver-007',
  name: 'Cost Optimization Oracle',
  trigger: 'onMonthlyTrendUpdate',
  inputs: ['shipmentData', 'historical'],
  logic: ({ shipmentData }) => detectSavingsRoutes(shipmentData),
  voiceLine: (result) =>
    `Ka-ching! A ${result.savingsPercentage}% drop spotted on ${result.route} if you swap to ${result.modeChange}. That’s enough for office snacks *and* ego boosts.`,
  sass: true
};

const allMoScripts = [mo_FWD_EFFICIENCY, mo_COST_ALERT];

const moScriptStructure = `
type MoScript = {
  id: string;
  name: string;
  trigger: string; // What event/context it responds to
  inputs: string[];
  logic: (inputs: Record<string, any>) => any;
  voiceLine?: (result: any) => string;
  sass?: boolean; // Soul-Aligned Security Scan
};
`.trim();

const MoScriptCard: React.FC<{ script: MoScript }> = ({ script }) => {
    const [isRunning, setIsRunning] = useState(false);
    const [resultMessage, setResultMessage] = useState('');

    const handleRun = () => {
        setIsRunning(true);
        setResultMessage('');

        // Simulate async execution
        setTimeout(() => {
            const mockInputs = { shipmentData: [], historical: [] }; // Provide dummy inputs
            const result = script.logic(mockInputs);
            if (script.voiceLine) {
                setResultMessage(script.voiceLine(result));
            }
            setIsRunning(false);
        }, 1500);
    };
    
    // Convert the logic function to a string for display
    const logicString = script.logic.toString().replace(/^.*{\s*|\s*}$/g, '').trim();

    return (
        <div className="grid-card rounded-lg shadow p-6 flex flex-col">
            <div className="flex items-center justify-between mb-3">
                <h3 className="text-xl font-bold text-white">{script.name}</h3>
                {script.sass && (
                     <span className="bg-cyan-800 text-cyan-200 text-xs font-medium px-2.5 py-1 rounded-full flex items-center">
                        <i className="fas fa-shield-alt mr-1.5"></i>SASS Enabled
                    </span>
                )}
            </div>
            <div className="text-sm text-gray-400 mb-4 font-mono">{script.id}</div>
            
            <div className="mb-4">
                <p className="text-gray-300"><strong className="text-purple-400">Trigger:</strong> {script.trigger}</p>
                <p className="text-gray-300"><strong className="text-purple-400">Inputs:</strong> {script.inputs.join(', ')}</p>
            </div>

            <div className="mb-4">
                <p className="text-gray-300 font-medium mb-2 text-purple-400">Logic:</p>
                <pre className="bg-gray-900/70 p-3 rounded-md text-gray-300 text-xs overflow-x-auto">
                    <code>{logicString}</code>
                </pre>
            </div>

            <div className="mt-auto">
                <button
                    onClick={handleRun}
                    disabled={isRunning}
                    className="w-full bg-purple-600 text-white py-2 px-4 rounded-lg font-medium text-sm flex items-center justify-center hover:bg-purple-700 transition-colors disabled:bg-gray-600 disabled:cursor-wait"
                >
                    {isRunning ? (
                        <><i className="fas fa-spinner fa-spin mr-2"></i>Executing...</>
                    ) : (
                        <><i className="fas fa-play mr-2"></i>Run Simulation</>
                    )}
                </button>
            </div>
            
            {resultMessage && (
                 <div className="mt-4 p-3 bg-green-900/50 border border-green-700 rounded-md">
                    <p className="text-sm text-green-300 italic">
                        <i className="fas fa-comment-dots mr-2"></i>
                        <strong>Woo says:</strong> "{resultMessage}"
                    </p>
                </div>
            )}
        </div>
    );
};


const MoScriptPage: React.FC = () => {
    return (
        <div>
            <PageTitle title="MoScript Playground" subtitle="Experience the core building blocks of the GRID." />
            
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Structure Column */}
                <div className="lg:col-span-1">
                     <h3 className="text-2xl font-bold text-white mb-4">Core Structure</h3>
                     <div className="grid-card p-6 rounded-lg">
                        <p className="text-gray-400 mb-4">
                            A `MoScript` is a self-contained, executable unit of symbolic logic. Each script has a defined trigger, inputs, and a covenant-aligned `voiceLine` for reporting results.
                        </p>
                         <pre className="bg-gray-900/70 p-4 rounded-md text-gray-300 text-sm overflow-x-auto">
                            <code>{moScriptStructure}</code>
                        </pre>
                     </div>
                </div>
                
                {/* Examples Column */}
                <div className="lg:col-span-2">
                    <h3 className="text-2xl font-bold text-white mb-4">Live Examples</h3>
                    <div className="space-y-6">
                        {allMoScripts.map(script => (
                            <MoScriptCard key={script.id} script={script} />
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default MoScriptPage;

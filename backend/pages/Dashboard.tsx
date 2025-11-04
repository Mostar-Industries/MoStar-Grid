import React, { useEffect, useState, useMemo } from 'react';
import ScrollCard from '../components/ScrollCard';
import { ServiceHealthCard } from '../components/ServiceHealthCard';
import { scrollsData } from '../data/scrolls';
import { wooInterpret } from '../lib/mostar/WooInterpreter';
import { codexData } from '../data/mogrid_u_codex';
import { Scroll } from '../types/moscript';
import { Interpretation } from '../lib/mostar/WooInterpreter';
import { StatPayload, ServicePayload, EventPayload } from '../types';
import { Sparkline } from '../components/Sparkline';

const PageTitle: React.FC<{ title: string; children?: React.ReactNode }> = ({ title, children }) => (
    <div className="mb-6 flex justify-between items-center">
        <h2 className="text-2xl font-bold text-white">{title}</h2>
        {children && <div className="flex space-x-2">{children}</div>}
    </div>
);

interface DashboardProps {
  onOpenTrainingModal: () => void;
  stats: StatPayload | null;
  services: (ServicePayload & { history: number[] })[];
  events: EventPayload[];
  isSentinelMode: boolean;
}

const Dashboard: React.FC<DashboardProps> = ({ onOpenTrainingModal, stats, services, events, isSentinelMode }) => {
    const [interpretations, setInterpretations] = useState<Record<string, Interpretation>>({});

    useEffect(() => {
        const scrollInterpretations: Record<string, Interpretation> = {};
        for (const scroll of scrollsData) {
            scrollInterpretations[scroll.id] = wooInterpret(scroll, codexData);
        }
        setInterpretations(scrollInterpretations);
    }, []);
    
    const handleRunScroll = (scroll: Scroll) => {
        alert(`Simulating run for scroll: "${scroll.name}"\n\nCode:\n${scroll.code}`);
    };

    const avgP95History = useMemo(() => {
        if (!services || services.length === 0 || !services[0].history) return [];
        
        const numPoints = services[0].history.length;
        const avgHistory: number[] = [];

        for (let i = 0; i < numPoints; i++) {
            const points = services.map(s => s.history[i]).filter(p => typeof p === 'number');
            if (points.length > 0) {
                const avg = points.reduce((sum, val) => sum + val, 0) / points.length;
                avgHistory.push(avg);
            } else {
                 avgHistory.push(0); 
            }
        }
        return avgHistory;
    }, [services]);

    return (
        <div>
            <PageTitle title="Covenant Registry" />
            
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
                <div className="lg:col-span-2">
                    <div className="grid [grid-template-columns:repeat(auto-fill,minmax(280px,1fr))] gap-4">
                        {services.map(s => <ServiceHealthCard key={s.name} {...s} />)}
                    </div>
                </div>
                 <div className="lg:col-span-1">
                     <div className="rounded-xl border border-white/10 bg-white/5 p-4 h-full flex flex-col min-h-[300px]">
                        <h3 className="font-semibold text-white mb-2">Overall Grid Latency (p95 Avg)</h3>
                        <div className="flex-grow flex items-center justify-center text-purple-400">
                            <Sparkline data={avgP95History} width={300} height={200} />
                        </div>
                    </div>
                </div>
            </div>
            
             <PageTitle title="Covenant Registry: Core Scrolls" />
             <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
                {scrollsData.map(scroll => 
                    interpretations[scroll.id] && (
                        <ScrollCard 
                            key={scroll.id} 
                            scroll={scroll} 
                            interpretation={interpretations[scroll.id]} 
                            onRun={handleRunScroll}
                            isSentinelMode={isSentinelMode}
                        />
                    )
                )}
             </div>
        </div>
    );
};

export default Dashboard;
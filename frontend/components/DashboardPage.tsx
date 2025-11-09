import React, { useState, useEffect } from 'react';
import TickerFeed from './TickerFeed';
import StatsCard from './StatsCard';
import { KpiCard } from './KpiCard';
import { ServiceHealthCard } from './ServiceHealthCard';
import { EventTicker } from './EventTicker';
import KnowledgeCard from './KnowledgeCard';
import ScrollCard from './ScrollCard'; // New import for ScrollCard
import { StatusIndicatorCard } from './StatusIndicatorCard'; // New import for StatusIndicatorCard
import KnowledgeGraph from './KnowledgeGraph'; // Import the new graph component
import { mockTickerStats, mockEventLog, mockDashboardStats, mockServiceHealth, mockKnowledgeCardsData, mockScrolls, mockInterpretations, mockGraphData } from '../data/mockData';
import { StatPayload, EventPayload } from '../types';

const DashboardPage: React.FC = () => {
    const [stats, setStats] = useState<StatPayload | null>(null);
    const [events, setEvents] = useState<EventPayload[]>([]);
    const [latestEvent, setLatestEvent] = useState<EventPayload | undefined>(undefined);

    // Mock KPI data for sparklines
    const [kpiData, setKpiData] = useState({
        coherenceHistory: [0.9, 0.92, 0.93, 0.95, 0.98, 0.97, 0.99],
        qpsHistory: [8, 9, 10, 11, 12, 11, 13],
        agentConnectHistory: [200, 210, 205, 215, 220, 218, 225],
    });

    useEffect(() => {
        // Simulate real-time updates for ticker and events
        const interval = setInterval(() => {
            // Update mock stats slightly
            const newStats = {
                ...mockTickerStats,
                coherence: Math.min(1, mockTickerStats.coherence + (Math.random() - 0.5) * 0.01),
                qps: Math.max(5, mockTickerStats.qps + (Math.random() - 0.5) * 0.5),
                activeNodes: mockTickerStats.activeNodes + Math.floor((Math.random() - 0.5) * 3),
            };
            setStats(newStats);

            // Add a new random event
            const newEvent: EventPayload = {
                ts: new Date().toISOString(),
                level: Math.random() > 0.8 ? 'error' : Math.random() > 0.5 ? 'warn' : 'info',
                text: `Dynamic event: ${Math.random().toFixed(4)}`,
            };
            setEvents((prev) => [newEvent, ...prev].slice(0, 10)); // Keep last 10 events
            setLatestEvent(newEvent);

            // Update KPI histories
            setKpiData(prev => ({
                coherenceHistory: [...prev.coherenceHistory.slice(1), newStats.coherence],
                qpsHistory: [...prev.qpsHistory.slice(1), newStats.qps],
                agentConnectHistory: [...prev.agentConnectHistory.slice(1), newStats.activeNodes],
            }));
        }, 5000); // Every 5 seconds

        // Initial load
        setStats(mockTickerStats);
        setEvents(mockEventLog);
        setLatestEvent(mockEventLog[0]);

        return () => clearInterval(interval);
    }, []);

    return (
        <div className="flex flex-col p-4 md:p-8 max-w-[calc(100vw-270px)] mx-auto space-y-8">
            {/* Ticker Feed */}
            <div className="bg-gray-900 rounded-lg shadow-custom overflow-hidden">
                <TickerFeed stats={stats} latestEvent={latestEvent} />
            </div>

            {/* Core Stats & KPIs */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {/* Stats Cards */}
                {mockDashboardStats.map((card, index) => (
                    <StatsCard key={index} {...card} />
                ))}

                {/* KPIs */}
                <KpiCard
                    title="Grid Coherence"
                    value={stats ? `${(stats.coherence * 100).toFixed(2)}` : 'N/A'}
                    unit="%"
                    history={kpiData.coherenceHistory.map(h => h * 100)} // Scale for display
                    valueColorClass="text-emerald-300"
                />
                <KpiCard
                    title="Avg. Query/Sec"
                    value={stats ? stats.qps.toFixed(1) : 'N/A'}
                    history={kpiData.qpsHistory}
                    valueColorClass="text-sky-300"
                />
                 <KpiCard
                    title="Active Agents"
                    value={stats ? stats.activeNodes.toString() : 'N/A'}
                    history={kpiData.agentConnectHistory}
                    valueColorClass="text-purple-300"
                />
                 <StatusIndicatorCard
                    title="Data Sovereignty Shield"
                    status="Online" // This could be dynamic based on a mock status
                    description="CARE principles actively enforced across all knowledge transactions."
                    lastChecked={new Date()}
                />
            </div>

            {/* New Knowledge Graph Visualization */}
            <div className="grid-card rounded-lg shadow p-4">
                <h3 className="text-xl font-bold text-white mb-4">Knowledge Fabric Visualization</h3>
                 <div className="knowledge-graph-container h-[500px]">
                    <KnowledgeGraph autoFetch={true} maxNodes={50} />
                </div>
            </div>

            {/* Service Health and Event Log */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2">
                    <h3 className="text-xl font-bold text-white mb-4">Core Service Health</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {mockServiceHealth.map((service, index) => (
                            <ServiceHealthCard key={index} {...service} />
                        ))}
                    </div>
                </div>
                <div>
                    <h3 className="text-xl font-bold text-white mb-4">Event Log</h3>
                    <EventTicker items={events} />
                </div>
            </div>

            {/* Knowledge Fabric & MoScript Scrolls */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                    <h3 className="text-xl font-bold text-white mb-4">Knowledge Fabric Nodes</h3>
                    <div className="grid grid-cols-1 gap-4">
                        {mockKnowledgeCardsData.map((data, index) => (
                            <KnowledgeCard key={index} {...data} />
                        ))}
                    </div>
                </div>
                <div>
                    <h3 className="text-xl font-bold text-white mb-4">MoScript Scrolls</h3>
                    <div className="grid grid-cols-1 gap-4">
                        {mockScrolls.map((scroll) => (
                            <ScrollCard key={scroll.id} scroll={scroll} interpretation={mockInterpretations[scroll.id]} />
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default DashboardPage;
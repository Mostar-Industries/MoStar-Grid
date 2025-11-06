import React from 'react';
import { marked } from 'marked';
import { statsCards as mockStatsCards } from '../data/mockData';
import { knowledgeCards } from '../data/knowledgeCards';
import { codex } from '../data/codex';
import StatsCard from '../components/StatsCard';
import KnowledgeCard from '../components/KnowledgeCard';
import TickerFeed from '../components/TickerFeed';
import { KpiCard } from '../components/KpiCard';
import { ServiceHealthCard } from '../components/ServiceHealthCard';
import { EventTicker } from '../components/EventTicker';
import { useGridStream } from '../hooks/useGridStream';

const Dashboard: React.FC = () => {
  const { stats, services, events } = useGridStream();

  const coherenceHistory = React.useMemo(() => [...(new Array(20).fill(0.99)), ...(stats ? [stats.coherence] : [])].slice(-20), [stats]);
  const qpsHistory = React.useMemo(() => [...(new Array(20).fill(2100000)), ...(stats ? [stats.qps / 1000] : [])].slice(-20), [stats]);
  
  const welcomeHtml = marked.parse(codex.welcome);

  return (
    <div className="p-6 h-full overflow-y-auto">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-6 mb-6">
        {mockStatsCards.map((card, index) => (
          <StatsCard key={index} {...card} />
        ))}
      </div>

      <div className="mb-6">
        <h3 className="text-xl font-bold text-white mb-4">Live Grid Telemetry</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <KpiCard title="Grid Coherence" value={`${((stats?.coherence ?? 0.9998) * 100).toFixed(2)}`} unit="%" history={coherenceHistory.map(v => v * 100)} />
            <KpiCard title="Queries Per Second" value={`${((stats?.qps ?? 2100000) / 1000).toFixed(1)}k`} history={qpsHistory} />
            <KpiCard title="Active Neural Nodes" value={stats?.activeNodes?.toString() ?? '427'} history={[...coherenceHistory].reverse().map(v => v * 427)} />
            <KpiCard title="Consciousness Uploads" value={stats?.uploads?.toLocaleString() ?? '1,283'} history={[...qpsHistory].reverse().map(v => v/50000)} />
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <div className="lg:col-span-2">
            <h3 className="text-xl font-bold text-white mb-4">Service Health</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {services.map(s => <ServiceHealthCard key={s.name} {...s} history={coherenceHistory} />)}
            </div>
        </div>
        <div>
            <h3 className="text-xl font-bold text-white mb-4">Event Stream</h3>
            <EventTicker items={events} />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div>
          <h3 className="text-xl font-bold text-white mb-4">Welcome to the MoStar GRID</h3>
          <div
            className="grid-card p-6 rounded-lg prose prose-invert max-w-none"
            dangerouslySetInnerHTML={{ __html: welcomeHtml }}
          />
        </div>
        <div>
          <h3 className="text-xl font-bold text-white mb-4">Featured Knowledge</h3>
          <div className="space-y-4">
            {knowledgeCards.slice(0, 2).map(card => (
              <KnowledgeCard key={card.id} {...card} />
            ))}
          </div>
        </div>
      </div>
      
      <div className="fixed bottom-0 left-64 right-0 z-40">
        <TickerFeed stats={stats} latestEvent={events[0]} />
      </div>
    </div>
  );
};

export default Dashboard;

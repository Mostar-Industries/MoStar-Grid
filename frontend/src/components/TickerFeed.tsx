import React from 'react';
import { StatPayload, EventPayload } from '../types';

interface TickerFeedProps {
    stats: StatPayload | null;
    latestEvent: EventPayload | undefined;
}

const TickerFeed: React.FC<TickerFeedProps> = ({ stats, latestEvent }) => {
    const messages = [];

    if (stats) {
        const coherence = (stats.coherence * 100).toFixed(2);
        const qps = stats.qps.toFixed(1);
        messages.push(`[Mostar Feed] Grid sync stable – Neural nodes: ${stats.activeNodes} active – Coherence: ${coherence}% – QPS: ${qps}`);
    } else {
        messages.push('[Mostar Feed] Awaiting Grid connection...');
    }

    if (latestEvent) {
        const alertType = latestEvent.level === 'error' ? 'System Alert' : 'System Update';
        messages.push(`[${alertType}] ${latestEvent.text}`);
    }

    if (stats) {
        messages.push(`[Knowledge Base] Total indexed consciousness: ${stats.uploads.toLocaleString()}. Growth rate nominal.`);
    }

    const tickerContent = messages.join(' &nbsp;&nbsp;&nbsp; 🔸 &nbsp;&nbsp;&nbsp; ');

    return (
        <div className="ticker-feed">
            <div className="ticker-content" dangerouslySetInnerHTML={{ __html: tickerContent }} />
        </div>
    );
};

export default TickerFeed;
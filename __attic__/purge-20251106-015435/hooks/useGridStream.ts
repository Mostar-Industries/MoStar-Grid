import { useState, useEffect } from 'react';
import { StatPayload, ServicePayload, EventPayload } from '../types';
import { availableAgents } from '../data/availableAgents';

const serviceNames: ServicePayload['name'][] = ["API", "DB", "Cache", "Queue", "Auth", "Models"];

// Function to generate a single random service payload
const generateServicePayload = (name: ServicePayload['name']): ServicePayload => {
    const status = Math.random() < 0.9 ? 'ok' : Math.random() < 0.95 ? 'warn' : 'fail';
    const rps = Math.random() * 100 + 50;
    const p50 = Math.random() * 50 + 20;
    return {
        name,
        status,
        rps,
        p50,
        p95: p50 + Math.random() * 100,
        errorRate: status === 'ok' ? Math.random() * 0.01 : Math.random() * 0.1,
        uptime: Math.floor(Math.random() * 1000000) + 86400,
        version: `1.${Math.floor(Math.random() * 5)}.${Math.floor(Math.random() * 10)}`,
    };
};

// Function to generate a single random event payload
const generateEventPayload = (): EventPayload => {
    const level = Math.random() < 0.8 ? 'info' : Math.random() < 0.95 ? 'warn' : 'error';
    const agent = availableAgents[Math.floor(Math.random() * availableAgents.length)];
    const texts = {
        info: [`Scroll execution approved for agent '${agent}'.`, `New consciousness uploaded. Size: ${(Math.random() * 10).toFixed(2)}GB`, `Grid coherence re-calibrated.`],
        warn: [`High latency detected on DB node. p95 > 200ms`, `Cache eviction rate at 85% capacity.`, `Soulprint validation for '${agent}' took > 500ms.`],
        error: [`Failed to execute MoScript for '${agent}'. Resonance below threshold.`, `Soulprint verification failed for unknown entity.`, `DB connection pool exhausted. Requests failing.`]
    };
    return {
        ts: new Date().toISOString(),
        level,
        text: texts[level][Math.floor(Math.random() * texts[level].length)]
    };
};

export function useGridStream() {
    const [stats, setStats] = useState<StatPayload | null>(null);
    const [services, setServices] = useState<ServicePayload[]>([]);
    const [events, setEvents] = useState<EventPayload[]>([]);

    useEffect(() => {
        const interval = setInterval(() => {
            // Update stats
            setStats(prev => ({
                activeNodes: Math.floor(Math.random() * 100) + 400,
                coherence: Math.random() * 0.02 + 0.98,
                qps: (prev?.qps || 2100000) + (Math.random() * 20000 - 10000),
                uploads: (prev?.uploads || 1283) + (Math.random() > 0.8 ? 1 : 0),
                soulprints: 3,
            }));

            // Update services
            setServices(serviceNames.map(generateServicePayload));

            // Update events
            if (Math.random() > 0.5) {
                setEvents(prev => [generateEventPayload(), ...prev].slice(0, 50));
            }

        }, 2000); // Update every 2 seconds

        // Initial data load
        setServices(serviceNames.map(generateServicePayload));


        return () => clearInterval(interval);
    }, []);

    return { stats, services, events };
}

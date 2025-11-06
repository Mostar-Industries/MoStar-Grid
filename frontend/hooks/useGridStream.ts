import { useState, useEffect } from 'react';
import { StatPayload, ServicePayload, EventPayload } from '../types';

export function useGridStream() {
  const [stats, setStats] = useState<StatPayload | null>(null);
  const [services, setServices] = useState<ServicePayload[]>([]);
  const [events, setEvents] = useState<EventPayload[]>([]);

  useEffect(() => {
    // Initialize with default values
    setStats({
      activeNodes: 410,
      coherence: 0.9904,
      qps: 2100000,
      uploads: 42,
      soulprints: 42,
    });

    setServices([
      { name: 'API', status: 'ok', rps: 1200, p50: 12, p95: 45, errorRate: 0.001, uptime: 86400, version: '1.0.0' },
      { name: 'DB', status: 'ok', rps: 800, p50: 8, p95: 25, errorRate: 0.0005, uptime: 86400 },
      { name: 'Cache', status: 'ok', rps: 5000, p50: 2, p95: 8, errorRate: 0, uptime: 86400 },
      { name: 'Queue', status: 'ok', rps: 300, p50: 15, p95: 50, errorRate: 0.002, uptime: 86400 },
    ]);

    setEvents([
      { ts: new Date().toISOString(), level: 'info', text: 'Grid system initialized' },
      { ts: new Date().toISOString(), level: 'info', text: 'All services healthy' },
    ]);

    // TODO: Connect to WebSocket for real-time updates
    // const ws = new WebSocket('ws://localhost:7000/ws');
    // ws.onmessage = (event) => {
    //   const data = JSON.parse(event.data);
    //   // Update state based on message type
    // };
    // return () => ws.close();
  }, []);

  return { stats, services, events };
}

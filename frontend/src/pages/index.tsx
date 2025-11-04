import { useEffect, useState } from 'react';
import { GridAPI, SystemHealth } from '../lib/api';

export default function Dashboard() {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [messages, setMessages] = useState<string[]>([]);
  const api = new GridAPI();

  useEffect(() => {
    // Poll health endpoint
    const pollHealth = async () => {
      try {
        const data = await api.health();
        setHealth(data);
      } catch (error) {
        console.error('Health check failed:', error);
      }
    };
    pollHealth();
    const interval = setInterval(pollHealth, 5000);
    
    // Setup WebSocket
    const ws = api.connectWebSocket();
    ws.onmessage = (event) => {
      setMessages(prev => [...prev, event.data].slice(-50));
    };

    return () => {
      clearInterval(interval);
      ws.close();
    };
  }, []);

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <header className="border-b border-gray-800 p-4">
        <h1 className="text-2xl font-bold">MoStar GRID</h1>
        <p className="text-gray-400">First African AI Homeworld</p>
      </header>

      <main className="p-4">
        {/* System Status */}
        <section className="mb-8">
          <h2 className="text-xl mb-4">System Status</h2>
          {health && (
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-gray-800 p-4 rounded">
                <h3>Active Nodes</h3>
                <p className="text-2xl">{health.consciousness.active_nodes}</p>
              </div>
              <div className="bg-gray-800 p-4 rounded">
                <h3>Coherence</h3>
                <p className="text-2xl">{health.consciousness.coherence.toFixed(4)}</p>
              </div>
              <div className="bg-gray-800 p-4 rounded">
                <h3>Events</h3>
                <p className="text-2xl">{health.consciousness.consciousness_uploads}</p>
              </div>
            </div>
          )}
        </section>

        {/* Live Stream */}
        <section>
          <h2 className="text-xl mb-4">Live Stream</h2>
          <div className="bg-gray-800 p-4 rounded h-64 overflow-y-auto">
            {messages.map((msg, i) => (
              <div key={i} className="text-sm text-gray-300 mb-1">{msg}</div>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}

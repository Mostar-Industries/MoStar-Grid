import { useEffect, useState } from "react";
import { StatPayload, ServicePayload, EventPayload } from '../types';

export function useSSE(url: string) {
  const [stats, setStats] = useState<StatPayload | null>(null);
  const [services, setServices] = useState<Record<string, ServicePayload & { history: number[] }>>({});
  const [events, setEvents] = useState<EventPayload[]>([]);
  
  useEffect(() => {
    const handleStats = (e: Event) => {
      const data = (e as CustomEvent).detail as StatPayload;
      setStats(data);
    };

    const handleService = (e: Event) => {
      const d = (e as CustomEvent).detail as ServicePayload;
      setServices(prev => {
        const old = prev[d.name]?.history ?? [];
        const hist = [...old.slice(-89), d.p95]; // keep ~90 points
        return { ...prev, [d.name]: { ...d, history: hist } };
      });
    };

    const handleEvent = (e: Event) => {
      const d = (e as CustomEvent).detail as EventPayload;
      setEvents(prev => [d, ...prev].slice(0, 50)); // keep 50 most recent
    };
    
    // In a real app, we'd use EventSource. Here, we listen to custom events
    // dispatched by our client-side simulator.
    window.addEventListener("sse:stats", handleStats);
    window.addEventListener("sse:service", handleService);
    window.addEventListener("sse:event", handleEvent);

    return () => {
      window.removeEventListener("sse:stats", handleStats);
      window.removeEventListener("sse:service", handleService);
      window.removeEventListener("sse:event", handleEvent);
    };
  }, [url]);

  // Fix: Added explicit types to the sort callback parameters to resolve type inference issues.
  return { stats, services: Object.values(services).sort((a: ServicePayload, b: ServicePayload) => a.name.localeCompare(b.name)), events };
}
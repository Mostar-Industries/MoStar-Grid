import { useEffect, useRef, useState } from 'react';
import { WS_BASE } from '../lib/env';

export type GridStreamStatus = 'offline' | 'connecting' | 'online' | 'error';

export interface GridStreamData {
  ts: number;
  gridLatencyMs: number;
  cpu: number;
  mem: number;
  service: string;
  event: string;
  mock?: boolean;
}

/**
 * Real-time Grid telemetry via WebSocket
 * 
 * Dev:  Connects to /ws/live-stream via Vite proxy
 * Prod: Connects to VITE_WS_URL/live-stream
 */
export function useGridStream() {
  const [data, setData] = useState<GridStreamData | null>(null);
  const [status, setStatus] = useState<GridStreamStatus>('offline');
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectRef = useRef(0);

  useEffect(() => {
    let closed = false;

    const connect = () => {
      setStatus('connecting');
      const proto = location.protocol === 'https:' ? 'wss' : 'ws';

      // dev: WS_BASE='/ws' -> ws(s)://host/ws/live-stream
      // prod: WS_BASE='wss://api.example.com/ws' -> append '/live-stream'
      const abs = WS_BASE.startsWith('ws') || WS_BASE.startsWith('wss');
      const url = abs
        ? `${WS_BASE.replace(/\/$/, '')}/live-stream`
        : `${proto}://${location.host}${WS_BASE}/live-stream`;

      console.log('[useGridStream] Connecting to:', url);

      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        if (!closed) {
          console.log('[useGridStream] Connected');
          setStatus('online');
          reconnectRef.current = 0;
        }
      };

      ws.onmessage = (ev) => {
        try {
          const parsed = JSON.parse(ev.data);
          setData(parsed);
        } catch (e) {
          console.error('[useGridStream] Failed to parse message:', e);
        }
      };

      ws.onerror = (err) => {
        console.error('[useGridStream] WebSocket error:', err);
        setStatus('error');
      };

      ws.onclose = () => {
        if (closed) return;
        console.log('[useGridStream] Disconnected, reconnecting...');
        setStatus('offline');
        const backoff = Math.min(1000 * (2 ** reconnectRef.current), 8000);
        reconnectRef.current += 1;
        setTimeout(connect, backoff);
      };
    };

    connect();

    return () => {
      closed = true;
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  return { data, status };
}

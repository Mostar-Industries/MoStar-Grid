// API Types matching backend models
export interface GridEvent {
    event_type: string;
    source_agent: string;
    location: string;
    data: Record<string, any>;
    priority?: string;
}

export interface GridResponse {
    event_id: string;
    status: string;
    resonance_score: number;
    woo_judgment: string;
}

export interface SystemHealth {
    status: string;
    db: {
        connected: boolean;
        pool_min: number | null;
        pool_max: number | null;
    };
    consciousness: {
        active_nodes: number;
        coherence: number;
        consciousness_uploads: number;
    };
}

// API Client class
export class GridAPI {
    private baseUrl: string;

    constructor() {
        this.baseUrl = (process.env.NEXT_PUBLIC_BACKEND_URL as string) || 'http://localhost:7000';
    }

    async health(): Promise<SystemHealth> {
        try {
            const response = await fetch(`${this.baseUrl.replace(/\/$/, '')}/health`, { credentials: 'same-origin' });
            if (!response.ok) {
                const text = await response.text().catch(()=>null);
                throw new Error(`Backend responded ${response.status}: ${text || response.statusText}`);
            }
            return await response.json();
        } catch (err: any) {
            // Provide a clearer error for the caller/UI
            const msg = err?.message ? err.message : String(err);
            console.error('GridAPI.health error:', msg);
            throw new Error(`Network error when contacting backend (${this.baseUrl}): ${msg}`);
        }
    }

    async submitEvent(event: GridEvent): Promise<GridResponse> {
        try {
            const response = await fetch(`${this.baseUrl.replace(/\/$/, '')}/events`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(event),
                credentials: 'same-origin'
            });
            if (!response.ok) {
                const text = await response.text().catch(()=>null);
                throw new Error(`Backend responded ${response.status}: ${text || response.statusText}`);
            }
            return await response.json();
        } catch (err: any) {
            const msg = err?.message ? err.message : String(err);
            console.error('GridAPI.submitEvent error:', msg);
            throw new Error(`Failed to submit event: ${msg}`);
        }
    }

    async generateData(params: {
        size?: number;
        batch_size?: number;
        scenario?: string;
        load_db?: boolean;
        truncate?: boolean;
        export?: boolean;
    }): Promise<{status: string; cmd: string}> {
        try {
            const response = await fetch(`${this.baseUrl.replace(/\/$/, '')}/api/generate-synthetic-data`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(params)
            });
            if (!response.ok) {
                const text = await response.text().catch(()=>null);
                throw new Error(`Backend responded ${response.status}: ${text || response.statusText}`);
            }
            return await response.json();
        } catch (err: any) {
            console.error('GridAPI.generateData error:', err?.message ?? err);
            throw err;
        }
    }

    connectWebSocket(): WebSocket {
        // Choose ws or wss based on baseUrl protocol
        try {
            const url = new URL(this.baseUrl);
            const protocol = url.protocol === 'https:' ? 'wss:' : 'ws:';
            const host = url.host;
            const wsUrl = `${protocol}//${host}/ws/live-stream`;
            return new WebSocket(wsUrl);
        } catch (err) {
            // Fallback to ws with host-only
            const host = (this.baseUrl.replace(/^https?:\/\//, '')).replace(/\/$/, '');
            return new WebSocket(`ws://${host}/ws/live-stream`);
        }
    }
}

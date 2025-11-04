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
        this.baseUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:7000';
    }

    async health(): Promise<SystemHealth> {
        const response = await fetch(`${this.baseUrl}/health`);
        return response.json();
    }

    async submitEvent(event: GridEvent): Promise<GridResponse> {
        const response = await fetch(`${this.baseUrl}/events`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(event)
        });
        return response.json();
    }

    async generateData(params: {
        size?: number;
        batch_size?: number;
        scenario?: string;
        load_db?: boolean;
        truncate?: boolean;
        export?: boolean;
    }): Promise<{status: string; cmd: string}> {
        const response = await fetch(`${this.baseUrl}/api/generate-synthetic-data`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(params)
        });
        return response.json();
    }

    connectWebSocket(): WebSocket {
        const ws = new WebSocket(`ws://${new URL(this.baseUrl).host}/ws/live-stream`);
        return ws;
    }
}

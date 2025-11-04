
let simulatorInterval: number | null = null;
let uptime = 0;

function send(event: string, payload: any) {
    window.dispatchEvent(new CustomEvent(`sse:${event}`, { detail: payload }));
}

export function startMetricSimulator() {
    if (simulatorInterval) {
        return; // Already running
    }

    const serviceTemplates = [
        ["API", "ok"], ["DB", "ok"], ["Cache", "ok"], ["Queue", "ok"],
        ["Auth", "warn"], ["Models", "ok"], ["Files", "ok"]
    ];

    simulatorInterval = window.setInterval(() => {
        const now = new Date().toISOString();
        uptime += 2;

        // Roll-up stats
        send("stats", {
            activeNodes: 400 + Math.floor(Math.random() * 40),
            coherence: 0.985 + Math.random() * 0.015,
            qps: 180 + Math.random() * 40,
            uploads: 1283,
            soulprints: 3,
        });

        // Services
        for (const [name, base] of serviceTemplates) {
            let status = base as "ok" | "warn" | "fail";
            // Make failures rare but possible
            if (Math.random() < 0.01) status = "fail"; 
            else if (name === 'Auth' && Math.random() < 0.1) status = 'warn'; // Auth is more sensitive
            
            send("service", {
                name,
                status,
                rps: +(50 + Math.random() * 70).toFixed(1),
                p50: 30 + Math.random() * (status === 'warn' ? 80 : 30),
                p95: 80 + Math.random() * (status === 'fail' ? 250 : 60),
                errorRate: status === "fail" ? 0.1 + Math.random() * 0.1 : (status === "warn" ? 0.01 + Math.random() * 0.02 : Math.random() * 0.005),
                uptime: uptime,
                version: "2.1." + Math.floor(Math.random() * 10)
            });
        }

        // Occasional event
        if (Math.random() < 0.25) {
            const levels = ["info", "warn", "error"];
            const level = levels[Math.floor(Math.random() * (uptime < 20 ? 1.5 : 3))]; // More info/warn at start
            let text = "Deploy completed to Models v2.1.x";
            if (level === 'warn') text = "DB connection latency spiking";
            if (level === 'error') text = `Auth service p95 breached threshold (>300ms)`;
            
            send("event", { ts: now, level, text });
        }
    }, 2000);
}

export function stopMetricSimulator() {
    if (simulatorInterval) {
        clearInterval(simulatorInterval);
        simulatorInterval = null;
        uptime = 0;
    }
}

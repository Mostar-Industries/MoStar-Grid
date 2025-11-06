module.exports = [
"[externals]/react/jsx-dev-runtime [external] (react/jsx-dev-runtime, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("react/jsx-dev-runtime", () => require("react/jsx-dev-runtime"));

module.exports = mod;
}),
"[project]/Documents/GitHub/MoStar-Grid/frontend/src/lib/api.ts [ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

// API Types matching backend models
__turbopack_context__.s([
    "GridAPI",
    ()=>GridAPI
]);
class GridAPI {
    baseUrl;
    constructor(){
        this.baseUrl = ("TURBOPACK compile-time value", "http://localhost:8080") || 'http://localhost:7000';
    }
    async health() {
        try {
            const response = await fetch(`${this.baseUrl.replace(/\/$/, '')}/health`, {
                credentials: 'same-origin'
            });
            if (!response.ok) {
                const text = await response.text().catch(()=>null);
                throw new Error(`Backend responded ${response.status}: ${text || response.statusText}`);
            }
            return await response.json();
        } catch (err) {
            // Provide a clearer error for the caller/UI
            const msg = err?.message ? err.message : String(err);
            console.error('GridAPI.health error:', msg);
            throw new Error(`Network error when contacting backend (${this.baseUrl}): ${msg}`);
        }
    }
    async submitEvent(event) {
        try {
            const response = await fetch(`${this.baseUrl.replace(/\/$/, '')}/events`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(event),
                credentials: 'same-origin'
            });
            if (!response.ok) {
                const text = await response.text().catch(()=>null);
                throw new Error(`Backend responded ${response.status}: ${text || response.statusText}`);
            }
            return await response.json();
        } catch (err) {
            const msg = err?.message ? err.message : String(err);
            console.error('GridAPI.submitEvent error:', msg);
            throw new Error(`Failed to submit event: ${msg}`);
        }
    }
    async generateData(params) {
        try {
            const response = await fetch(`${this.baseUrl.replace(/\/$/, '')}/api/generate-synthetic-data`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(params)
            });
            if (!response.ok) {
                const text = await response.text().catch(()=>null);
                throw new Error(`Backend responded ${response.status}: ${text || response.statusText}`);
            }
            return await response.json();
        } catch (err) {
            console.error('GridAPI.generateData error:', err?.message ?? err);
            throw err;
        }
    }
    connectWebSocket() {
        // Choose ws or wss based on baseUrl protocol
        try {
            const url = new URL(this.baseUrl);
            const protocol = url.protocol === 'https:' ? 'wss:' : 'ws:';
            const host = url.host;
            const wsUrl = `${protocol}//${host}/ws/live-stream`;
            return new WebSocket(wsUrl);
        } catch (err) {
            // Fallback to ws with host-only
            const host = this.baseUrl.replace(/^https?:\/\//, '').replace(/\/$/, '');
            return new WebSocket(`ws://${host}/ws/live-stream`);
        }
    }
}
}),
"[project]/Documents/GitHub/MoStar-Grid/frontend/src/pages/index.tsx [ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>Dashboard
]);
var __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__ = __turbopack_context__.i("[externals]/react/jsx-dev-runtime [external] (react/jsx-dev-runtime, cjs)");
var __TURBOPACK__imported__module__$5b$externals$5d2f$react__$5b$external$5d$__$28$react$2c$__cjs$29$__ = __turbopack_context__.i("[externals]/react [external] (react, cjs)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$GitHub$2f$MoStar$2d$Grid$2f$frontend$2f$src$2f$lib$2f$api$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Documents/GitHub/MoStar-Grid/frontend/src/lib/api.ts [ssr] (ecmascript)");
;
;
;
function Dashboard() {
    const [health, setHealth] = (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react__$5b$external$5d$__$28$react$2c$__cjs$29$__["useState"])(null);
    const [messages, setMessages] = (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react__$5b$external$5d$__$28$react$2c$__cjs$29$__["useState"])([]);
    const api = new __TURBOPACK__imported__module__$5b$project$5d2f$Documents$2f$GitHub$2f$MoStar$2d$Grid$2f$frontend$2f$src$2f$lib$2f$api$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__["GridAPI"]();
    (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react__$5b$external$5d$__$28$react$2c$__cjs$29$__["useEffect"])(()=>{
        // Poll health endpoint
        const pollHealth = async ()=>{
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
        ws.onmessage = (event)=>{
            setMessages((prev)=>[
                    ...prev,
                    event.data
                ].slice(-50));
        };
        return ()=>{
            clearInterval(interval);
            ws.close();
        };
    }, []);
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("div", {
        className: "min-h-screen bg-gray-900 text-white",
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("header", {
                className: "border-b border-gray-800 p-4",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("h1", {
                        className: "text-2xl font-bold",
                        children: "MoStar GRID"
                    }, void 0, false, {
                        fileName: "[project]/Documents/GitHub/MoStar-Grid/frontend/src/pages/index.tsx",
                        lineNumber: 37,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("p", {
                        className: "text-gray-400",
                        children: "First African AI Homeworld"
                    }, void 0, false, {
                        fileName: "[project]/Documents/GitHub/MoStar-Grid/frontend/src/pages/index.tsx",
                        lineNumber: 38,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/Documents/GitHub/MoStar-Grid/frontend/src/pages/index.tsx",
                lineNumber: 36,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("main", {
                className: "p-4",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("section", {
                        className: "mb-8",
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("h2", {
                                className: "text-xl mb-4",
                                children: "System Status"
                            }, void 0, false, {
                                fileName: "[project]/Documents/GitHub/MoStar-Grid/frontend/src/pages/index.tsx",
                                lineNumber: 44,
                                columnNumber: 11
                            }, this),
                            health && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("div", {
                                className: "grid grid-cols-3 gap-4",
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("div", {
                                        className: "bg-gray-800 p-4 rounded",
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("h3", {
                                                children: "Active Nodes"
                                            }, void 0, false, {
                                                fileName: "[project]/Documents/GitHub/MoStar-Grid/frontend/src/pages/index.tsx",
                                                lineNumber: 48,
                                                columnNumber: 17
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("p", {
                                                className: "text-2xl",
                                                children: health.consciousness.active_nodes
                                            }, void 0, false, {
                                                fileName: "[project]/Documents/GitHub/MoStar-Grid/frontend/src/pages/index.tsx",
                                                lineNumber: 49,
                                                columnNumber: 17
                                            }, this)
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/Documents/GitHub/MoStar-Grid/frontend/src/pages/index.tsx",
                                        lineNumber: 47,
                                        columnNumber: 15
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("div", {
                                        className: "bg-gray-800 p-4 rounded",
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("h3", {
                                                children: "Coherence"
                                            }, void 0, false, {
                                                fileName: "[project]/Documents/GitHub/MoStar-Grid/frontend/src/pages/index.tsx",
                                                lineNumber: 52,
                                                columnNumber: 17
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("p", {
                                                className: "text-2xl",
                                                children: health.consciousness.coherence.toFixed(4)
                                            }, void 0, false, {
                                                fileName: "[project]/Documents/GitHub/MoStar-Grid/frontend/src/pages/index.tsx",
                                                lineNumber: 53,
                                                columnNumber: 17
                                            }, this)
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/Documents/GitHub/MoStar-Grid/frontend/src/pages/index.tsx",
                                        lineNumber: 51,
                                        columnNumber: 15
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("div", {
                                        className: "bg-gray-800 p-4 rounded",
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("h3", {
                                                children: "Events"
                                            }, void 0, false, {
                                                fileName: "[project]/Documents/GitHub/MoStar-Grid/frontend/src/pages/index.tsx",
                                                lineNumber: 56,
                                                columnNumber: 17
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("p", {
                                                className: "text-2xl",
                                                children: health.consciousness.consciousness_uploads
                                            }, void 0, false, {
                                                fileName: "[project]/Documents/GitHub/MoStar-Grid/frontend/src/pages/index.tsx",
                                                lineNumber: 57,
                                                columnNumber: 17
                                            }, this)
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/Documents/GitHub/MoStar-Grid/frontend/src/pages/index.tsx",
                                        lineNumber: 55,
                                        columnNumber: 15
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/Documents/GitHub/MoStar-Grid/frontend/src/pages/index.tsx",
                                lineNumber: 46,
                                columnNumber: 13
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/Documents/GitHub/MoStar-Grid/frontend/src/pages/index.tsx",
                        lineNumber: 43,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("section", {
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("h2", {
                                className: "text-xl mb-4",
                                children: "Live Stream"
                            }, void 0, false, {
                                fileName: "[project]/Documents/GitHub/MoStar-Grid/frontend/src/pages/index.tsx",
                                lineNumber: 65,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("div", {
                                className: "bg-gray-800 p-4 rounded h-64 overflow-y-auto",
                                children: messages.map((msg, i)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("div", {
                                        className: "text-sm text-gray-300 mb-1",
                                        children: msg
                                    }, i, false, {
                                        fileName: "[project]/Documents/GitHub/MoStar-Grid/frontend/src/pages/index.tsx",
                                        lineNumber: 68,
                                        columnNumber: 15
                                    }, this))
                            }, void 0, false, {
                                fileName: "[project]/Documents/GitHub/MoStar-Grid/frontend/src/pages/index.tsx",
                                lineNumber: 66,
                                columnNumber: 11
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/Documents/GitHub/MoStar-Grid/frontend/src/pages/index.tsx",
                        lineNumber: 64,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/Documents/GitHub/MoStar-Grid/frontend/src/pages/index.tsx",
                lineNumber: 41,
                columnNumber: 7
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/Documents/GitHub/MoStar-Grid/frontend/src/pages/index.tsx",
        lineNumber: 35,
        columnNumber: 5
    }, this);
}
}),
"[externals]/next/dist/shared/lib/no-fallback-error.external.js [external] (next/dist/shared/lib/no-fallback-error.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/shared/lib/no-fallback-error.external.js", () => require("next/dist/shared/lib/no-fallback-error.external.js"));

module.exports = mod;
}),
];

//# sourceMappingURL=%5Broot-of-the-server%5D__7beda079._.js.map
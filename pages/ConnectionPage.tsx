import React, { useState } from 'react';

const PageTitle: React.FC<{ title: string; children?: React.ReactNode }> = ({ title, children }) => (
    <div className="mb-6">
        <h2 className="text-3xl font-bold text-white">{title}</h2>
        {children && <div className="mt-2 text-gray-400 max-w-4xl">{children}</div>}
    </div>
);

const CodeBlock: React.FC<{ code: string; language?: string; filename?: string }> = ({ code, language, filename }) => {
    const [copied, setCopied] = useState(false);
    const handleCopy = () => {
        navigator.clipboard.writeText(code);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div className="bg-gray-900/70 rounded-lg my-4">
            {filename && (
                <div className="px-4 py-2 border-b border-gray-700 text-xs text-gray-400 font-mono">
                    {filename}
                </div>
            )}
            <div className="relative p-4">
                <pre className="text-gray-300 text-sm overflow-x-auto">
                    <code className={`language-${language}`}>{code.trim()}</code>
                </pre>
                <button
                    onClick={handleCopy}
                    className="absolute top-2 right-2 bg-gray-700 hover:bg-gray-600 text-gray-300 px-2 py-1 rounded-md text-xs"
                >
                    {copied ? <><i className="fas fa-check mr-1 text-green-400"></i>Copied!</> : <><i className="fas fa-copy mr-1"></i>Copy</>}
                </button>
            </div>
        </div>
    );
};

const PhaseSection: React.FC<{ phase: number; title: string; children: React.ReactNode }> = ({ phase, title, children }) => (
    <div className="grid-card rounded-lg p-6 mb-8">
        <h3 className="text-xl font-bold text-purple-400 mb-1">Phase {phase}</h3>
        <h4 className="text-2xl font-semibold text-white mb-4">{title}</h4>
        <div className="prose prose-invert text-gray-300 max-w-none">{children}</div>
    </div>
);

const ConnectionPage: React.FC = () => {
    const [status, setStatus] = useState<'Idle' | 'Testing...' | 'Success' | 'Failed'>('Idle');
    const [response, setResponse] = useState('');

    const handleTest = async () => {
        setStatus('Testing...');
        setResponse('');
        try {
            const res = await fetch('/api/health');
            const data = await res.json();
            if (!res.ok) {
                throw new Error(`Server responded with status: ${res.status} ${res.statusText}`);
            }
            setStatus('Success');
            setResponse(JSON.stringify(data, null, 2));
        } catch (error: any) {
            setStatus('Failed');
            setResponse(`Error: ${error.message}. This is expected if the Python server is not running or the Vite proxy is not configured.`);
        }
    };
    
    const statusClasses = {
        'Idle': 'border-gray-600',
        'Testing...': 'border-blue-500 text-blue-300',
        'Success': 'border-green-500 text-green-300',
        'Failed': 'border-red-500 text-red-300',
    };

    return (
        <div>
            <PageTitle title="Backend Alignment Guide">
                <p>This guide provides a dockerless integration plan for connecting the React frontend to the Python API services. Follow these phases to establish a local development environment.</p>
            </PageTitle>

            <div className="grid-card rounded-lg p-6 mb-8">
                <h3 className="text-xl font-semibold text-white mb-3">API Gateway Health Check</h3>
                <p className="text-gray-400 mb-4">Click the button to send a `GET` request to `/api/health`. This tests the Vite proxy and the running FastAPI server.</p>
                <div className="flex items-center gap-4">
                    <button 
                        onClick={handleTest}
                        disabled={status === 'Testing...'}
                        className="bg-teal-600 text-white px-4 py-2 rounded-md hover:bg-teal-700 disabled:opacity-50 disabled:cursor-wait"
                    >
                        {status === 'Testing...' ? (
                            <><i className="fas fa-spinner fa-spin mr-2" />Pinging API...</>
                        ) : (
                            <><i className="fas fa-network-wired mr-2" />Test API Connection</>
                        )}
                    </button>
                    <div className={`flex-grow p-3 bg-gray-900 rounded-md text-sm border ${statusClasses[status]}`}>
                        <p>Status: <span className="font-mono">{status}</span></p>
                        {response && <pre className="mt-2 text-gray-400 whitespace-pre-wrap">{response}</pre>}
                    </div>
                </div>
            </div>

            <PhaseSection phase={1} title="Minimal Python API Gateway (FastAPI)">
                <p>First, set up a small API gateway that the frontend can talk to locally. This provides a health check, note management endpoints, and a placeholder for scroll execution.</p>
                <h5 className="font-semibold text-lg mt-4 mb-2 text-white">Directory Structure</h5>
                <CodeBlock language="text" code={`
backend/
└── server/
    ├── main.py
    ├── db.py
    ├── requirements.txt
    └── .env.example
                `} />
                 <h5 className="font-semibold text-lg mt-4 mb-2 text-white">Dependencies</h5>
                <CodeBlock language="text" filename="backend/server/requirements.txt" code={`
fastapi==0.115.0
uvicorn[standard]==0.30.0
python-dotenv==1.0.1
pydantic-settings==2.4.0
psycopg[binary]==3.2.1
                `} />
                <h5 className="font-semibold text-lg mt-4 mb-2 text-white">Environment Configuration</h5>
                <CodeBlock language="text" filename="backend/server/.env.example" code={`
# Server-only secrets — DO NOT COMMIT real values
DATABASE_URL=postgresql://<user>:<pass>@<ep-host>.neon.tech/neondb?sslmode=require
ALLOW_ORIGINS=http://localhost:3000
MOCK_MODE=false
                `} />
                <h5 className="font-semibold text-lg mt-4 mb-2 text-white">Main Application</h5>
                <CodeBlock language="python" filename="backend/server/main.py" code={`
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# ... (full content from alignment guide)
@app.get("/api/health")
async def health():
    return {"ok": True, "mock": "settings.MOCK_MODE"}
# ... etc.
                `} />
            </PhaseSection>

            <PhaseSection phase={2} title="Vite Proxy to Python API">
                <p>Edit `vite.config.ts` to add a proxy. This forwards any browser request to `/api` to your local Python server running on port 8000.</p>
                <CodeBlock language="typescript" filename="vite.config.ts" code={`
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000, // or your frontend port
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
})
                `} />
            </PhaseSection>

             <PhaseSection phase={5} title="Runbook (Windows PowerShell)">
                 <p>Follow these steps to start both the backend and frontend servers.</p>
                 <h5 className="font-semibold text-lg mt-4 mb-2 text-white">A. Start Backend (Python)</h5>
                <CodeBlock language="powershell" code={`
# From project root
cd backend/server
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt

# Set environment variables for the session
$env:DATABASE_URL="your_neon_db_connection_string"
$env:ALLOW_ORIGINS="http://localhost:3000"
$env:MOCK_MODE="false"

uvicorn main:app --reload --port 8000
                `} />
                <h5 className="font-semibold text-lg mt-4 mb-2 text-white">B. Start Frontend (Vite)</h5>
                <CodeBlock language="powershell" code={`
# From project root
npm install
npm run dev
                `} />
                 <p className="mt-4">After running both, visit your frontend URL (e.g., `http://localhost:3000`) and use the health check button at the top of this page to verify the connection.</p>
             </PhaseSection>
        </div>
    );
};

export default ConnectionPage;
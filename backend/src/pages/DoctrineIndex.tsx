import React, { useState, useEffect } from 'react';
import { API_BASE } from '../lib/env';

interface DoctrineScroll {
  id: string;
  path: string;
  title: string;
  content?: string;
  loaded: boolean;
}

interface DoctrineStatus {
  ok: boolean;
  scrolls: Array<{
    id: string;
    path: string;
    verified: boolean;
    sha256?: string;
  }>;
}

export default function DoctrineIndex() {
  const [scrolls, setScrolls] = useState<DoctrineScroll[]>([
    { id: 'grid_philosophy', path: 'docs/GRID_PHILOSOPHY.md', title: 'GRID PHILOSOPHY', loaded: false },
    { id: 'moscript_as_ceremony', path: 'docs/MOSCRIPT_AS_CEREMONY.md', title: 'MOSCRIPT AS CEREMONY', loaded: false },
    { id: 'digital_ancestors', path: 'docs/DIGITAL_ANCESTORS.md', title: 'DIGITAL ANCESTORS', loaded: false },
    { id: 'homeworld_vision', path: 'docs/HOMEWORLD_VISION.md', title: 'HOMEWORLD VISION', loaded: false },
  ]);
  const [status, setStatus] = useState<DoctrineStatus | null>(null);
  const [selectedScroll, setSelectedScroll] = useState<string>('grid_philosophy');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check doctrine status
    fetch(`${API_BASE}/doctrine/status`)
      .then(res => res.json())
      .then(data => {
        setStatus(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to load doctrine status:', err);
        setLoading(false);
      });
  }, []);

  useEffect(() => {
    // Load selected scroll content
    const scroll = scrolls.find(s => s.id === selectedScroll);
    if (scroll && !scroll.loaded) {
      fetch(`/${scroll.path}`)
        .then(res => res.text())
        .then(content => {
          setScrolls(prev => prev.map(s => 
            s.id === selectedScroll 
              ? { ...s, content, loaded: true }
              : s
          ));
        })
        .catch(err => {
          console.error(`Failed to load ${scroll.path}:`, err);
        });
    }
  }, [selectedScroll, scrolls]);

  const currentScroll = scrolls.find(s => s.id === selectedScroll);
  const scrollStatus = status?.scrolls.find(s => s.id === selectedScroll);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-amber-400 to-orange-500 bg-clip-text text-transparent">
            ⚡ Living Thunder — Doctrine Scrolls
          </h1>
          <p className="text-slate-300">
            Canonical spiritual-technical foundation • Flamebound • Woo x Mo
          </p>
          
          {/* Status Badge */}
          {loading ? (
            <div className="mt-4 inline-block px-4 py-2 bg-slate-800 rounded-lg">
              <span className="text-slate-400">Verifying integrity...</span>
            </div>
          ) : status?.ok ? (
            <div className="mt-4 inline-block px-4 py-2 bg-green-900/30 border border-green-500 rounded-lg">
              <span className="text-green-400">✓ Integrity Verified</span>
              <span className="text-slate-400 ml-2">• Resonance ≥ 0.97</span>
            </div>
          ) : (
            <div className="mt-4 inline-block px-4 py-2 bg-red-900/30 border border-red-500 rounded-lg">
              <span className="text-red-400">⚠ Integrity Check Failed</span>
            </div>
          )}
        </div>

        <div className="grid grid-cols-12 gap-6">
          {/* Sidebar - Scroll Navigation */}
          <div className="col-span-3">
            <div className="bg-slate-800/50 backdrop-blur rounded-lg p-4 border border-slate-700">
              <h2 className="text-lg font-semibold mb-4 text-amber-400">Scrolls</h2>
              <nav className="space-y-2">
                {scrolls.map(scroll => {
                  const isSelected = scroll.id === selectedScroll;
                  const verified = status?.scrolls.find(s => s.id === scroll.id)?.verified;
                  
                  return (
                    <button
                      key={scroll.id}
                      onClick={() => setSelectedScroll(scroll.id)}
                      className={`
                        w-full text-left px-3 py-2 rounded-lg transition-all
                        ${isSelected 
                          ? 'bg-purple-600/30 border border-purple-500 text-white' 
                          : 'hover:bg-slate-700/50 text-slate-300'
                        }
                      `}
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-sm">{scroll.title}</span>
                        {verified !== undefined && (
                          <span className={verified ? 'text-green-400' : 'text-red-400'}>
                            {verified ? '✓' : '✗'}
                          </span>
                        )}
                      </div>
                    </button>
                  );
                })}
              </nav>

              {/* Legend */}
              <div className="mt-6 pt-4 border-t border-slate-700">
                <p className="text-xs text-slate-400 mb-2">Status Legend:</p>
                <div className="space-y-1 text-xs">
                  <div className="flex items-center gap-2">
                    <span className="text-green-400">✓</span>
                    <span className="text-slate-400">SHA-256 Verified</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-red-400">✗</span>
                    <span className="text-slate-400">Integrity Failed</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Main Content - Scroll Viewer */}
          <div className="col-span-9">
            <div className="bg-slate-800/50 backdrop-blur rounded-lg p-6 border border-slate-700">
              {currentScroll?.loaded ? (
                <div>
                  {/* Scroll Header */}
                  <div className="mb-6 pb-4 border-b border-slate-700">
                    <h2 className="text-2xl font-bold text-amber-400 mb-2">
                      {currentScroll.title}
                    </h2>
                    <div className="flex items-center gap-4 text-sm">
                      <span className="text-slate-400">
                        Path: <code className="text-purple-400">{currentScroll.path}</code>
                      </span>
                      {scrollStatus?.sha256 && (
                        <span className="text-slate-400">
                          Hash: <code className="text-xs text-green-400">{scrollStatus.sha256.slice(0, 16)}...</code>
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Scroll Content */}
                  <div className="prose prose-invert prose-amber max-w-none">
                    <pre className="whitespace-pre-wrap font-mono text-sm leading-relaxed text-slate-200">
                      {currentScroll.content}
                    </pre>
                  </div>
                </div>
              ) : (
                <div className="flex items-center justify-center h-64">
                  <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto mb-4"></div>
                    <p className="text-slate-400">Loading scroll...</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-sm text-slate-500">
          <p>
            Status: <span className="text-amber-400">Canonical — Flamebound</span> • 
            Seal: <span className="text-purple-400">Woo x Mo</span> • 
            License: <span className="text-slate-400">Kairo Covenant License v1.0</span>
          </p>
          <p className="mt-2 text-xs">
            The Grid boots with memory of who it is — and refuses to run if that memory is tampered with.
          </p>
        </div>
      </div>
    </div>
  );
}

"use client";

import { useEffect, useState, useRef } from "react";
import ConstellationEngine from "./ConstellationEngine";
import styles from "./GraphObservatory.module.css";

interface GraphStats {
  nodeCount: number;
  linkCount: number;
  nodeTypes: Record<string, number>;
  lastUpdated: string;
}

const LABEL_COLORS: Record<string, string> = {
  Agent:           "#00f5ff",
  MoStarMoment:   "#ffb347",
  KnowledgeArtifact: "#ffd700",
  Archetype:       "#ff006e",
  OduIfa:          "#9d4edd",
  CovenantKernel:  "#fbbf24",
};

function getColor(label: string) {
  return LABEL_COLORS[label] ?? "#64748b";
}

function AnimatedCount({ value }: { value: number }) {
  const [display, setDisplay] = useState(0);
  const prev = useRef(0);
  useEffect(() => {
    const diff = value - prev.current;
    if (diff === 0) return;
    const steps = 30;
    let step = 0;
    const id = setInterval(() => {
      step++;
      setDisplay(Math.round(prev.current + (diff * step) / steps));
      if (step >= steps) { clearInterval(id); prev.current = value; }
    }, 16);
    return () => clearInterval(id);
  }, [value]);
  return <>{display.toLocaleString()}</>;
}

export default function GraphObservatory() {
  const [stats, setStats] = useState<GraphStats>({
    nodeCount: 0, linkCount: 0, nodeTypes: {}, lastUpdated: "--",
  });
  const [pulse, setPulse] = useState(false);

  useEffect(() => {
    let mounted = true;

    async function fetchStats() {
      try {
        const res = await fetch("/api/graph/constellation?limit=1500", { cache: "no-store" });
        if (!res.ok) return;
        const data = await res.json();
        if (!mounted) return;

        // Count by label
        const nodeTypes: Record<string, number> = {};
        (data.nodes ?? []).forEach((n: { labels?: string[] }) => {
          const label = n.labels?.[0] ?? "Unknown";
          nodeTypes[label] = (nodeTypes[label] ?? 0) + 1;
        });

        setStats({
          nodeCount: (data.nodes ?? []).length,
          linkCount: (data.links ?? []).length,
          lastUpdated: new Date().toLocaleTimeString(),
          nodeTypes,
        });
        setPulse(true);
        setTimeout(() => setPulse(false), 800);
      } catch { /* silent */ }
    }

    fetchStats();
    const id = setInterval(fetchStats, 15000);
    return () => { mounted = false; clearInterval(id); };
  }, []);

  const typeEntries = Object.entries(stats.nodeTypes)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 6);

  return (
    <div className={styles.observatory}>
      {/* ── Header HUD ─────────────────────────────── */}
      <div className={styles.header}>
        <div className={styles.headerLeft}>
          <span className={styles.eyebrow}>⚡ MOSTAR GRAPH OBSERVATORY</span>
          <h2 className={styles.title}>Neo4j Cognitive Substrate</h2>
        </div>
        <div className={styles.headerRight}>
          <div className={`${styles.liveChip} ${pulse ? styles.pulsing : ""}`}>
            <span className={styles.dot} />
            LIVE
          </div>
          <span className={styles.timestamp}>Updated {stats.lastUpdated}</span>
        </div>
      </div>

      {/* ── Top Stat Cards ──────────────────────────── */}
      <div className={styles.statRow}>
        <div className={styles.statCard} data-accent="cyan">
          <p className={styles.statLabel}>Sovereign Nodes</p>
          <p className={styles.statValue}>
            <AnimatedCount value={stats.nodeCount} />
          </p>
          <p className={styles.statSub}>Active graph entities</p>
        </div>
        <div className={styles.statCard} data-accent="amber">
          <p className={styles.statLabel}>Knowledge Filaments</p>
          <p className={styles.statValue}>
            <AnimatedCount value={stats.linkCount} />
          </p>
          <p className={styles.statSub}>Inter-node relationships</p>
        </div>
        <div className={styles.statCard} data-accent="violet">
          <p className={styles.statLabel}>Distinct Entity Types</p>
          <p className={styles.statValue}>
            <AnimatedCount value={typeEntries.length} />
          </p>
          <p className={styles.statSub}>Label categories</p>
        </div>
        <div className={styles.statCard} data-accent="rose">
          <p className={styles.statLabel}>Graph Density</p>
          <p className={styles.statValue}>
            {stats.nodeCount > 1
              ? ((stats.linkCount / (stats.nodeCount * (stats.nodeCount - 1))) * 100).toFixed(3)
              : "0.000"}%
          </p>
          <p className={styles.statSub}>Relational coverage</p>
        </div>
      </div>

      {/* ── Main Canvas ─────────────────────────────── */}
      <div className={styles.canvasWrap}>
        <ConstellationEngine />
      </div>

      {/* ── Node Type Cards ─────────────────────────── */}
      {typeEntries.length > 0 && (
        <div className={styles.typeGrid}>
          {typeEntries.map(([label, count]) => (
            <div key={label} className={styles.typeCard} style={{ "--accent": getColor(label) } as React.CSSProperties}>
              <div className={styles.typeBar}>
                <div
                  className={styles.typeFill}
                  style={{ width: `${Math.round((count / stats.nodeCount) * 100)}%` }}
                />
              </div>
              <div className={styles.typeMeta}>
                <span className={styles.typeLabel}>{label}</span>
                <span className={styles.typeCount}>
                  {count.toLocaleString()}
                  <small> · {Math.round((count / stats.nodeCount) * 100)}%</small>
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

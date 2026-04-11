"use client";

import { useGridTelemetry } from "@/hooks/useGridTelemetry";
import styles from "./Neo4jMonitor.module.css";
import { CSSProperties, useMemo, useState, useEffect } from "react";

export default function Neo4jMonitor() {
    const { telemetry } = useGridTelemetry();
    const [pulse, setPulse] = useState(false);

    const neo4jStatus = telemetry?.backend?.data?.neo4j || "unknown";
    const ok = telemetry?.graph?.ok;
    const isStreaming = Boolean(ok) && ["connected", "online"].includes(String(neo4jStatus).toLowerCase());

    // Pulse on new moments
    const moments = telemetry?.graph.stats?.totalMoments || 0;
    useEffect(() => {
        if (moments > 0) {
            setPulse(true);
            const t = setTimeout(() => setPulse(false), 800);
            return () => clearTimeout(t);
        }
    }, [moments]);

    const stats: any = telemetry?.graph.stats || {};
    const layerNodes = telemetry?.graph?.layer_nodes || {};
    const relTypes = telemetry?.graph?.relationship_types || {};

    const totalNodes = stats.totalNodes || 0;
    const totalRels = stats.totalRelationships || 0;
    const density = stats.graphDensity || 0;
    const artifacts = stats.totalArtifacts || 0;
    const agents = stats.totalAgents || 0;
    const moments24h = stats.moments24h || 0;
    const resonance = stats.avgResonance || 0.85;

    const topLabels = useMemo(() =>
        Object.entries(layerNodes).sort((a, b) => b[1] - a[1]).slice(0, 5)
        , [layerNodes]);

    const topRels = useMemo(() =>
        Object.entries(relTypes).sort((a, b) => b[1] - a[1]).slice(0, 5)
        , [relTypes]);

    return (
        <div className={styles.observatoryContainer}>
            <header className={styles.observatoryHeader}>
                <div className={styles.titleGroup}>
                    <p className={styles.eyebrow}>⚡ MOSTAR GRAPH OBSERVATORY</p>
                    <h2 className={styles.title}>Neo4j Cognitive Substrate</h2>
                </div>
                <div className={`${styles.statusBadge} ${isStreaming ? styles.online : styles.offline}`}>
                    <div className={`${styles.pulseDot} ${pulse ? styles.activePulse : ""}`} />
                    <span>Executor {isStreaming ? "Linked" : "Disconnected"}</span>
                </div>
            </header>

            <div className={styles.obsGrid}>
                {/* Left: Scientific Specs */}
                <section className={styles.specSection}>
                    <div className={styles.specHeader}>
                        <span>❖</span>
                        <h3>Graph Instrumentation</h3>
                    </div>
                    <div className={styles.specMetricGrid}>
                        <div className={styles.specCard}>
                            <label>Global Nodes</label>
                            <strong>{totalNodes.toLocaleString()}</strong>
                        </div>
                        <div className={styles.specCard}>
                            <label>Relationships</label>
                            <strong>{totalRels.toLocaleString()}</strong>
                        </div>
                        <div className={styles.specCard}>
                            <label>Graph Density</label>
                            <strong>{density.toFixed(6)}</strong>
                        </div>
                        <div className={styles.specCard}>
                            <label>Knowledge Artifacts</label>
                            <strong>{artifacts.toLocaleString()}</strong>
                        </div>
                        <div className={styles.specCard}>
                            <label>Active Agents</label>
                            <strong>{agents.toLocaleString()}</strong>
                        </div>
                        <div className={styles.specCard}>
                            <label>Resonance field</label>
                            <strong>{(resonance * 100).toFixed(1)}%</strong>
                        </div>
                    </div>
                </section>

                {/* Center: Symbolic Labels (Constellation view style) */}
                <section className={styles.constellationSection}>
                    <div className={styles.specHeader}>
                        <span>✧</span>
                        <h3>Sovereign Labels</h3>
                    </div>
                    <div className={styles.labelConstellation}>
                        {topLabels.map(([label, count]) => (
                            <div key={label} className={styles.constellationNode} data-label={label}>
                                <div className={styles.nodeGlyph}>◉</div>
                                <div className={styles.nodeInfo}>
                                    <p className={styles.nodeLabel}>{label.replace(/_/g, " ")}</p>
                                    <p className={styles.nodeCount}>{count.toLocaleString()}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </section>

                {/* Right: Relationship Flows */}
                <section className={styles.flowSection}>
                    <div className={styles.specHeader}>
                        <span>⇌</span>
                        <h3>Relationship Flows</h3>
                    </div>
                    <div className={styles.flowList}>
                        {topRels.map(([rel, count]) => (
                            <div key={rel} className={styles.flowRow}>
                                <div className={styles.flowBase}>
                                    <span className={styles.flowName}>{rel}</span>
                                    <span className={styles.flowCount}>{count.toLocaleString()}</span>
                                </div>
                                <div className={styles.flowTrack}>
                                    <div
                                        className={styles.flowFill}
                                        style={{ "--width": `${Math.min(100, (count / totalRels) * 300)}%` } as CSSProperties}
                                    />
                                </div>
                            </div>
                        ))}
                    </div>
                </section>
            </div>

            <footer className={styles.observatoryFooter}>
                <div className={styles.footerMetric}>
                    <label>Moments / 24h</label>
                    <strong>{moments24h.toLocaleString()}</strong>
                </div>
                <div className={styles.footerMetric}>
                    <label>Distinct Initiators</label>
                    <strong>{stats.distinctInitiators ?? 0}</strong>
                </div>
                <div className={styles.heartbeatBlock}>
                    <span className={styles.heartbeatLabel}>EXECUTOR PULSE</span>
                    <div className={styles.heartbeatIcon}>⚡</div>
                </div>
            </footer>
        </div>
    );
}

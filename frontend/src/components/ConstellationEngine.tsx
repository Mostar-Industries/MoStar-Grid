"use client";

import React, { useEffect, useState, useMemo, useRef } from "react";
import ForceGraph3D, { ForceGraphMethods } from "react-force-graph-3d";
import * as THREE from "three";
import styles from "./ConstellationEngine.module.css";

interface GraphNode {
    id: string | number;
    name: string;
    labels: string[];
    resonance: number;
    timestamp?: string;
    x?: number;
    y?: number;
    z?: number;
}

interface GraphLink {
    source: string | number;
    target: string | number;
    rel: string;
}

export default function ConstellationEngine() {
    const fgRef = useRef<any>(null);
    const [graphData, setGraphData] = useState<{ nodes: GraphNode[]; links: GraphLink[] }>({ nodes: [], links: [] });
    const [loading, setLoading] = useState(true);

    const GRID_API = process.env.NEXT_PUBLIC_GRID_API_BASE || "http://127.0.0.1:7001";

    const fetchGraph = async () => {
        try {
            const res = await fetch(`${GRID_API}/api/v1/graph/constellation?limit=1500`, { cache: 'no-store' });
            if (res.ok) {
                const data = await res.json();
                setGraphData(data);
                setLoading(false);
            }
        } catch (err) {
            console.error("Constellation Fetch Error:", err);
        }
    };

    useEffect(() => {
        fetchGraph();
        const interval = setInterval(fetchGraph, 10000); // Poll every 10s
        return () => clearInterval(interval);
    }, []);

    const getNodeColor = (labels: string[]) => {
        if (labels.includes("Agent")) return "#00F5FF";       // Electric Cyan
        if (labels.includes("KnowledgeArtifact")) return "#FFD700"; // Solar Gold
        if (labels.includes("MoStarMoment")) return "#FFB347";      // Amber
        if (labels.includes("Archetype")) return "#FF006E";         // Crimson
        if (labels.includes("OduIfa")) return "#9D4EDD";            // Oracle Violet
        if (labels.includes("CovenantKernel")) return "#fbbf24";    // Gold
        return "#ffffff";
    };

    const getLinkColor = (rel: string) => {
        switch (rel) {
            case "INFLUENCES": return "#00c2ff";
            case "CONTRIBUTES_TO": return "#ffd700";
            case "CONSULTS_ORACLE": return "#9d4edd";
            case "TRIGGERS": return "#ffb347";
            case "EVOLVES_FROM": return "#10b981";
            default: return "rgba(255,255,255,0.2)";
        }
    };

    return (
        <div className={styles.container}>
            <header className={styles.overlay}>
                <div className={styles.hudLeft}>
                    <p className={styles.eyebrow}>NEO4J COGNITIVE SUBSTRATE</p>
                    <h2 className={styles.title}>Knowledge Constellation</h2>
                </div>
                <div className={styles.hudRight}>
                    <div className={styles.status}>
                        <div className={styles.dot} />
                        <span>Resonance Tracking Active</span>
                    </div>
                </div>
            </header>

            <ForceGraph3D
                ref={fgRef}
                graphData={graphData}
                backgroundColor="#020617"
                showNavInfo={false}

                // Node Appearance
                nodeLabel={(node: any) => `
                    <div style="background: rgba(0,0,0,0.8); padding: 8px; border: 1px solid #06b6d4; border-radius: 4px; color: white;">
                        <b style="color: #fbbf24">${node.labels[0]}</b><br/>
                        ${node.name}<br/>
                        <small>Resonance: ${node.resonance.toFixed(3)}</small>
                    </div>
                `}
                nodeThreeObject={(node: any) => {
                    const color = getNodeColor(node.labels);
                    const size = 3 + (node.resonance * 4);

                    // Create a grouping
                    const group = new THREE.Group();

                    // Core sphere
                    const geometry = new THREE.SphereGeometry(size, 16, 16);
                    const material = new THREE.MeshBasicMaterial({ color });
                    const sphere = new THREE.Mesh(geometry, material);
                    group.add(sphere);

                    // Add a glow halo if resonance is high
                    if (node.resonance > 0.7) {
                        const glowGeometry = new THREE.SphereGeometry(size * 1.5, 16, 16);
                        const glowMaterial = new THREE.MeshBasicMaterial({
                            color,
                            transparent: true,
                            opacity: 0.15
                        });
                        const glow = new THREE.Mesh(glowGeometry, glowMaterial);
                        group.add(glow);
                    }

                    return group;
                }}

                // Link Appearance
                linkWidth={1}
                linkColor={(link: any) => getLinkColor(link.rel)}
                linkDirectionalParticles={2}
                linkDirectionalParticleSpeed={0.005}
                linkDirectionalParticleWidth={1.5}
                linkDirectionalParticleColor={(link: any) => getLinkColor(link.rel)}

                // Physics Optimization
                d3VelocityDecay={0.3}
                onNodeClick={(node: any) => {
                    // Aim at node from outside it
                    const distance = 40;
                    const distRatio = 1 + distance / Math.hypot(node.x, node.y, node.z);
                    if (fgRef.current) {
                        fgRef.current.cameraPosition(
                            { x: node.x * distRatio, y: node.y * distRatio, z: node.z * distRatio },
                            node,
                            3000
                        );
                    }
                }}
            />

            <footer className={styles.footerOverlay}>
                <div className={styles.controlInfo}>
                    <span>[LMB] ROTATE</span>
                    <span>[RMB] PAN</span>
                    <span>[SCROLL] ZOOM</span>
                </div>
                <div className={styles.metrics}>
                    <span>Sovereign Entities: {graphData.nodes.length}</span>
                    <span>Knowledge Filaments: {graphData.links.length}</span>
                </div>
            </footer>
        </div>
    );
}

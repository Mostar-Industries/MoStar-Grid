"use client";

import { Html, OrbitControls, useGLTF } from "@react-three/drei";
import { Canvas, useFrame } from "@react-three/fiber";
import dynamic from "next/dynamic";
import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import * as THREE from "three";
import styles from "./ConstellationEngine.module.css";

const ForceGraph3D = dynamic(
    () => import("react-force-graph-3d").then((mod) => mod.default),
    { ssr: false }
);

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type ForceGraphRef = any;

interface GraphNode {
    id: string | number;
    name: string;
    labels: string[];
    resonance: number;
    x?: number;
    y?: number;
    z?: number;
}

interface GraphLink {
    source: string | number;
    target: string | number;
    rel: string;
}

interface BrainTelemetry {
    nodeCount: number;
    linkCount: number;
    avgResonance: number;
}


/* ──────────────────────────────────────────────────────
   BrainModel — fluid vertex displacement + telemetry
   ────────────────────────────────────────────────────── */
function BrainModel({ telemetry }: { telemetry: BrainTelemetry }) {
    const meshRef = useRef<THREE.Group>(null);
    const { scene } = useGLTF("/holo.glb");
    const [hovered, setHovered] = useState(false);
    const [tooltipPos, setTooltipPos] = useState<[number, number, number]>([0, 2.5, 0]);

    // Telemetry-derived intensities (clamped 0..1)
    const activity = Math.min(telemetry.nodeCount / 500, 1);
    const resonance = telemetry.avgResonance;

    const { brainModel, brainMaterials, originalPositions } = useMemo(() => {
        const cloned = scene.clone();
        const materials: THREE.MeshPhongMaterial[] = [];
        const positionsMap = new Map<THREE.BufferGeometry, Float32Array>();

        cloned.traverse((child) => {
            if (child instanceof THREE.Mesh) {
                const mat = new THREE.MeshPhongMaterial({
                    color: 0xff0000,
                    transparent: true,
                    opacity: 0.25,
                    wireframe: true,
                    side: THREE.DoubleSide,
                    emissive: 0x000000,
                    emissiveIntensity: 0.5,
                    shininess: 120,
                });
                child.material = mat;
                materials.push(mat);

                // Store original positions for physical displacement
                const posAttr = child.geometry.attributes.position;
                if (posAttr) {
                    positionsMap.set(child.geometry, (posAttr.array as Float32Array).slice());
                }
            }
        });
        return { 
            brainModel: cloned, 
            brainMaterials: materials, 
            originalPositions: positionsMap 
        };
    }, [scene]);

    // Reusable color objects to avoid allocations per frame
    const _hsl = useRef({ h: 0, s: 0, l: 0 });

    useFrame((state) => {
        const t = state.clock.getElapsedTime();
        if (meshRef.current) {
            meshRef.current.rotation.y += 0.003;
            // Physical growth pulse based on activity
            const scaleBase = 4;
            const pulse = 1 + Math.sin(t * 0.8) * 0.02 * activity;
            meshRef.current.scale.setScalar(scaleBase * pulse);
        }

        // 1. PHYSICAL VERTEX DISPLACEMENT (Water/Growth Effect)
        originalPositions.forEach((orig, geo) => {
            const posAttr = geo.attributes.position;
            const arr = posAttr.array as Float32Array;
            const waveFreq = 2.5 + activity * 2;
            const waveAmp = 0.02 + activity * 0.05;

            for (let i = 0; i < arr.length; i += 3) {
                const ox = orig[i];
                const oy = orig[i + 1];
                const oz = orig[i + 2];

                // Multi-frequency sine ripples (physical displacement)
                const dist = Math.sqrt(ox * ox + oy * oy + oz * oz);
                const offset = Math.sin(dist * waveFreq - t * 2) * waveAmp + 
                               Math.cos(ox * 2 + t) * (waveAmp * 0.5);
                
                // Displace along the normal (pseudo-normal using radial direction)
                const nx = ox / dist;
                const ny = oy / dist;
                const nz = oz / dist;

                arr[i]     = ox + nx * offset;
                arr[i + 1] = oy + ny * offset;
                arr[i + 2] = oz + nz * offset;
            }
            posAttr.needsUpdate = true;
        });

        // 2. MATERIAL VISUALS (Rainbow + Opacity)
        const cycleSpeed = 0.08 + activity * 0.04;
        const pulseRate = 1.5 + activity * 2;
        const baseEmissive = 0.3 + resonance * 0.5;

        brainMaterials.forEach((mat, i) => {
            const hue = ((t * cycleSpeed) + i * 0.15) % 1;
            mat.color.setHSL(hue, 0.85, 0.55);

            _hsl.current.h = hue;
            _hsl.current.s = 0.9;
            _hsl.current.l = 0.25;
            mat.emissive.setHSL(_hsl.current.h, _hsl.current.s, _hsl.current.l);

            mat.emissiveIntensity = baseEmissive + Math.sin(t * pulseRate + i * 0.15) * 0.25;
            mat.opacity = 0.18 + activity * 0.08 + Math.sin(t * 1.2 + i * 0.1) * 0.04;
        });
    });

    useEffect(() => {
        return () => { brainMaterials.forEach((m) => m.dispose()); };
    }, [brainMaterials]);

    const handlePointerOver = useCallback((e: THREE.Event & { point?: THREE.Vector3 }) => {
        setHovered(true);
        if (e.point) setTooltipPos([e.point.x, e.point.y + 0.5, e.point.z]);
        document.body.style.cursor = "pointer";
    }, []);

    const handlePointerOut = useCallback(() => {
        setHovered(false);
        document.body.style.cursor = "auto";
    }, []);

    return (
        <group ref={meshRef} scale={[4, 4, 4]}>
            <primitive
                object={brainModel}
                onPointerOver={handlePointerOver}
                onPointerOut={handlePointerOut}
            />
            {hovered && (
                <Html position={tooltipPos} center style={{ pointerEvents: "none" }}>
                    <div className={styles.tooltip}>
                        <p className={styles.tooltipTitle}>⚡ MoStar Neural Mesh</p>
                        <div className={styles.tooltipRow}>
                            <span>Sovereign Nodes</span>
                            <strong>{telemetry.nodeCount.toLocaleString()}</strong>
                        </div>
                        <div className={styles.tooltipRow}>
                            <span>Knowledge Links</span>
                            <strong>{telemetry.linkCount.toLocaleString()}</strong>
                        </div>
                        <div className={styles.tooltipRow}>
                            <span>Resonance Field</span>
                            <strong>{(resonance * 100).toFixed(1)}%</strong>
                        </div>
                        <div className={styles.tooltipBar}>
                            <div className={styles.tooltipFill} style={{ width: `${activity * 100}%` }} />
                        </div>
                        <small className={styles.tooltipHint}>Activity index</small>
                    </div>
                </Html>
            )}
        </group>
    );
}

export default function ConstellationEngine() {
    const fgRef = useRef<ForceGraphRef>(null);
    const [graphData, setGraphData] = useState<{ nodes: GraphNode[]; links: GraphLink[] }>({ nodes: [], links: [] });
    const [loading, setLoading] = useState(true);
    const [isClient, setIsClient] = useState(false);
    const [showGraph, setShowGraph] = useState(false);

    const CONSTELLATION_API = "/api/graph/constellation"; // always server-side proxied

    useEffect(() => {
        const timer = setTimeout(() => setIsClient(true), 0);
        return () => clearTimeout(timer);
    }, []);

    const fetchGraph = async () => {
        try {
            const res = await fetch(`${CONSTELLATION_API}?limit=1500`, { cache: "no-store" });
            if (res.ok) {
                const data = await res.json();
                setGraphData(data);
                setLoading(false);
            }
        } catch (err) {
            console.error("Constellation Fetch Error:", err);
            setLoading(false);
        }
    };

    useEffect(() => {
        if (!isClient) return;
        fetchGraph();
        const interval = setInterval(fetchGraph, 10000);
        return () => clearInterval(interval);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [isClient]);

    // Compute telemetry from live graph data
    const brainTelemetry = useMemo<BrainTelemetry>(() => {
        const nodes = graphData.nodes || [];
        const avgRes = nodes.length > 0
            ? nodes.reduce((s, n) => s + (n.resonance ?? 0.5), 0) / nodes.length
            : 0.5;
        return {
            nodeCount: nodes.length,
            linkCount: (graphData.links || []).length,
            avgResonance: avgRes,
        };
    }, [graphData]);

    const getNodeColor = (labels: string[]) => {
        if (labels.includes("Agent")) return "#00F5FF";
        if (labels.includes("KnowledgeArtifact")) return "#FFD700";
        if (labels.includes("MoStarMoment")) return "#FFB347";
        if (labels.includes("Archetype")) return "#FF006E";
        if (labels.includes("OduIfa")) return "#9D4EDD";
        if (labels.includes("CovenantKernel")) return "#fbbf24";
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

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const nodeThreeObject = (node: any) => {
        const color = getNodeColor(node.labels || []);
        const geo = new THREE.SphereGeometry(4, 12, 12);
        const mat = new THREE.MeshBasicMaterial({ color });
        return new THREE.Mesh(geo, mat);
    };

    return (
        <div className={styles.container}>
            <header className={styles.overlay}>
                <div className={styles.hudLeft}>
                    <p className={styles.eyebrow}>NEO4J COGNITIVE SUBSTRATE</p>
                    <h2 className={styles.title}>Neural Mesh</h2>
                </div>
                <div className={styles.hudRight}>
                    <div className={styles.status}>
                        <div className={styles.dot} />
                        <span>Resonance Tracking Active</span>
                    </div>
                    <button
                        onClick={() => setShowGraph((v) => !v)}
                        style={{ marginLeft: "1rem", padding: "0.3rem 0.8rem", background: "rgba(0,200,255,0.15)", border: "1px solid #00c8ff", color: "#00c8ff", borderRadius: "4px", cursor: "pointer", fontSize: "0.72rem", letterSpacing: "0.1em" }}
                    >
                        {showGraph ? "BRAIN" : "GRAPH"}
                    </button>
                </div>
            </header>

            {loading && (
                <div className={styles.loadingOverlay}>
                    <div className={styles.spinner} />
                    <span>Syncing with Neo4j constellation...</span>
                </div>
            )}

            {isClient && showGraph ? (
                <ForceGraph3D
                    ref={fgRef}
                    graphData={graphData}
                    backgroundColor="#020617"
                    showNavInfo={false}
                    // eslint-disable-next-line @typescript-eslint/no-explicit-any
                    nodeLabel={(node: any) => `
                        <div style="background:rgba(0,0,0,0.8);padding:8px;border:1px solid #06b6d4;border-radius:4px;color:white;">
                            <b style="color:#fbbf24">${node.labels?.[0] ?? "Node"}</b><br/>
                            ${node.name}<br/>
                            <small>Resonance: ${(node.resonance ?? 0).toFixed(3)}</small>
                        </div>
                    `}
                    nodeThreeObject={nodeThreeObject}
                    linkWidth={1}
                    // eslint-disable-next-line @typescript-eslint/no-explicit-any
                    linkColor={(link: any) => getLinkColor(link.rel)}
                    linkDirectionalParticles={2}
                    linkDirectionalParticleSpeed={0.005}
                    linkDirectionalParticleWidth={1.5}
                    // eslint-disable-next-line @typescript-eslint/no-explicit-any
                    linkDirectionalParticleColor={(link: any) => getLinkColor(link.rel)}
                    d3VelocityDecay={0.3}
                    // eslint-disable-next-line @typescript-eslint/no-explicit-any
                    onNodeClick={(node: any) => {
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
            ) : (
                <Canvas
                    camera={{ position: [0, 0, 6], fov: 50 }}
                    style={{ width: "100%", height: "100%" }}
                >
                    <ambientLight intensity={0.3} />
                    <pointLight position={[10, 10, 10]} intensity={0.8} color={0x4df5ff} />
                    <pointLight position={[-8, -5, 5]} intensity={0.4} color={0x9d4edd} />
                    <React.Suspense fallback={null}>
                        <BrainModel telemetry={brainTelemetry} />
                    </React.Suspense>
                    <OrbitControls enableZoom={true} enablePan={false} autoRotate={false} />
                </Canvas>
            )}

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

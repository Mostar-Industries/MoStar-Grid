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
   Simplex-style 3D noise (compact, no deps)
   ────────────────────────────────────────────────────── */
function hash3(x: number, y: number, z: number) {
    let h = x * 374761393 + y * 668265263 + z * 1274126177;
    h = ((h ^ (h >> 13)) * 1274126177) | 0;
    return (h ^ (h >> 16)) / 2147483648;
}

function smoothNoise3(x: number, y: number, z: number): number {
    const ix = Math.floor(x), iy = Math.floor(y), iz = Math.floor(z);
    const fx = x - ix, fy = y - iy, fz = z - iz;
    const sx = fx * fx * (3 - 2 * fx);
    const sy = fy * fy * (3 - 2 * fy);
    const sz = fz * fz * (3 - 2 * fz);
    const n000 = hash3(ix, iy, iz), n100 = hash3(ix + 1, iy, iz);
    const n010 = hash3(ix, iy + 1, iz), n110 = hash3(ix + 1, iy + 1, iz);
    const n001 = hash3(ix, iy, iz + 1), n101 = hash3(ix + 1, iy, iz + 1);
    const n011 = hash3(ix, iy + 1, iz + 1), n111 = hash3(ix + 1, iy + 1, iz + 1);
    return (
        n000 * (1 - sx) * (1 - sy) * (1 - sz) + n100 * sx * (1 - sy) * (1 - sz) +
        n010 * (1 - sx) * sy * (1 - sz) + n110 * sx * sy * (1 - sz) +
        n001 * (1 - sx) * (1 - sy) * sz + n101 * sx * (1 - sy) * sz +
        n011 * (1 - sx) * sy * sz + n111 * sx * sy * sz
    );
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
    const density = Math.min(telemetry.linkCount / 1000, 1);
    const resonance = telemetry.avgResonance;

    const { brainModel, brainMeshes, brainMaterials, originalPositions } = useMemo(() => {
        const cloned = scene.clone();
        const materials: THREE.MeshPhongMaterial[] = [];
        const meshes: THREE.Mesh[] = [];
        const origPos: Float32Array[] = [];

        cloned.traverse((child) => {
            if (child instanceof THREE.Mesh) {
                const mat = new THREE.MeshPhongMaterial({
                    color: 0x76f2ff,
                    transparent: true,
                    opacity: 0.22,
                    wireframe: true,
                    side: THREE.DoubleSide,
                    emissive: 0x0a3a4f,
                    emissiveIntensity: 0.3,
                    shininess: 120,
                });
                child.material = mat;
                materials.push(mat);
                meshes.push(child);
                // Store original vertex positions for displacement
                const geo = child.geometry;
                if (geo.attributes.position) {
                    origPos.push(new Float32Array(geo.attributes.position.array));
                }
            }
        });
        return { brainModel: cloned, brainMeshes: meshes, brainMaterials: materials, originalPositions: origPos };
    }, [scene]);

    useFrame((state) => {
        const t = state.clock.getElapsedTime();
        if (meshRef.current) meshRef.current.rotation.y += 0.003;

        // Fluid vertex displacement — the "growing mind" water effect
        const waveSpeed = 0.6 + activity * 0.4;       // faster with more nodes
        const waveAmplitude = 0.04 + density * 0.06;   // bigger waves with more links
        const noiseScale = 1.2 + resonance * 0.8;      // noisier with higher resonance

        brainMeshes.forEach((mesh, mi) => {
            const geo = mesh.geometry;
            const pos = geo.attributes.position;
            const orig = originalPositions[mi];
            if (!pos || !orig) return;

            for (let i = 0; i < pos.count; i++) {
                const ox = orig[i * 3], oy = orig[i * 3 + 1], oz = orig[i * 3 + 2];
                // 3D noise displacement along vertex normal direction
                const n = smoothNoise3(
                    ox * noiseScale + t * waveSpeed,
                    oy * noiseScale + t * waveSpeed * 0.7,
                    oz * noiseScale + t * waveSpeed * 0.5
                );
                const displacement = (n - 0.5) * 2 * waveAmplitude;
                // Displace along the vertex direction from center (radial)
                const len = Math.sqrt(ox * ox + oy * oy + oz * oz) || 1;
                pos.setXYZ(i,
                    ox + (ox / len) * displacement,
                    oy + (oy / len) * displacement,
                    oz + (oz / len) * displacement
                );
            }
            pos.needsUpdate = true;
            geo.computeVertexNormals();
        });

        // Telemetry-driven material pulsing
        const pulseRate = 1.5 + activity * 2;
        const baseEmissive = 0.3 + resonance * 0.5;
        brainMaterials.forEach((mat, i) => {
            mat.emissiveIntensity = baseEmissive + Math.sin(t * pulseRate + i * 0.15) * 0.25;
            mat.opacity = 0.15 + activity * 0.08 + Math.sin(t * 1.2 + i * 0.1) * 0.04;
            // Shift color from cyan to brighter teal as activity grows
            const r = 0.46 + activity * 0.1;
            const g = 0.95;
            const b = 1.0 - activity * 0.15;
            mat.color.setRGB(r, g, b);
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
        <group ref={meshRef}>
            <primitive
                object={brainModel}
                scale={[4, 4, 4]}
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

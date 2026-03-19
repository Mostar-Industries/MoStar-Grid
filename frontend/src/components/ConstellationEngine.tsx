"use client";

import { OrbitControls, useGLTF } from "@react-three/drei";
import { Canvas, useFrame } from "@react-three/fiber";
import dynamic from "next/dynamic";
import React, { useEffect, useMemo, useRef, useState } from "react";
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

function BrainModel() {
    const meshRef = useRef<THREE.Group>(null);
    const { scene } = useGLTF("/holo.glb");

    const { brainModel, brainMaterials } = useMemo(() => {
        const cloned = scene.clone();
        const materials: THREE.MeshPhongMaterial[] = [];
        cloned.traverse((child) => {
            if (child instanceof THREE.Mesh) {
                const mat = new THREE.MeshPhongMaterial({
                    color: 0x76f2ff,
                    transparent: true,
                    opacity: 0.22,
                    wireframe: true,
                    side: THREE.DoubleSide,
                    emissive: 0x0a3a4f,
                    emissiveIntensity: 0.8,
                    shininess: 100,
                });
                child.material = mat;
                materials.push(mat);
            }
        });
        return { brainModel: cloned, brainMaterials: materials };
    }, [scene]);

    useFrame((state) => {
        const t = state.clock.getElapsedTime();
        if (meshRef.current) meshRef.current.rotation.y += 0.004;
        brainMaterials.forEach((mat, i) => {
            mat.emissiveIntensity = 0.65 + Math.sin(t * 2.2 + i * 0.12) * 0.35;
            mat.opacity = 0.16 + Math.sin(t * 1.6 + i * 0.07) * 0.05;
        });
    });

    useEffect(() => {
        return () => { brainMaterials.forEach((m) => m.dispose()); };
    }, [brainMaterials]);

    return (
        <group ref={meshRef}>
            <primitive object={brainModel} scale={[4, 4, 4]} />
        </group>
    );
}

export default function ConstellationEngine() {
    const fgRef = useRef<ForceGraphRef>(null);
    const [graphData, setGraphData] = useState<{ nodes: GraphNode[]; links: GraphLink[] }>({ nodes: [], links: [] });
    const [loading, setLoading] = useState(true);
    const [isClient, setIsClient] = useState(false);
    const [showGraph, setShowGraph] = useState(false);

    const GRID_API = process.env.NEXT_PUBLIC_GRID_API_BASE || "http://localhost:8001";

    useEffect(() => {
        const timer = setTimeout(() => setIsClient(true), 0);
        return () => clearTimeout(timer);
    }, []);

    const fetchGraph = async () => {
        try {
            const res = await fetch(`${GRID_API}/api/v1/graph/constellation?limit=1500`, { cache: "no-store" });
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
                    <h2 className={styles.title}>Hyper-Spine</h2>
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
                    <React.Suspense fallback={null}>
                        <BrainModel />
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

'use client';

import { Html, OrbitControls, Text, useGLTF } from '@react-three/drei';
import { Canvas, useFrame } from '@react-three/fiber';
import { Suspense, useEffect, useMemo, useRef, useState } from 'react';
import * as THREE from 'three';
import styles from './BrainVisualization.module.css';

interface MomentData {
  id: string;
  content: string;
  timestamp: string;
  position: [number, number, number];
  intensity: number;
  category: string;
}

function BrainMesh() {
  const meshRef = useRef<THREE.Group>(null);

  // Load the holo.glb brain model
  const { scene } = useGLTF('/holo.glb');

  const { brainModel, brainMaterials } = useMemo(() => {
    const cloned = scene.clone();
    const materials: THREE.MeshPhongMaterial[] = [];

    cloned.traverse((child) => {
      if (child instanceof THREE.Mesh) {
        const material = new THREE.MeshPhongMaterial({
          color: 0x76f2ff,
          transparent: true,
          opacity: 0.22,
          wireframe: true,
          side: THREE.DoubleSide,
          emissive: 0x0a3a4f,
          emissiveIntensity: 0.8,
          shininess: 100,
        });

        child.material = material;
        materials.push(material);
      }
    });

    return { brainModel: cloned, brainMaterials: materials };
  }, [scene]);

  const circuitPaths = useMemo(() => {
    return Array.from({ length: 14 }, (_, pathIndex) => {
      const points = Array.from({ length: 28 }, (_, pointIndex) => {
        const t = pointIndex / 27;
        const theta = t * Math.PI * 2.2 + pathIndex * 0.42;
        const phi = Math.PI * (0.33 + 0.34 * Math.sin(pathIndex * 0.7 + t * Math.PI * 1.8));
        const radius = 1.42 + 0.18 * Math.sin(pathIndex + t * 9);

        return new THREE.Vector3(
          radius * Math.sin(phi) * Math.cos(theta),
          radius * Math.cos(phi) * 1.08,
          radius * Math.sin(phi) * Math.sin(theta),
        );
      });

      const positions = new Float32Array(points.length * 3);
      points.forEach((point, i) => {
        positions[i * 3] = point.x;
        positions[i * 3 + 1] = point.y;
        positions[i * 3 + 2] = point.z;
      });

      return { points, positions };
    });
  }, []);

  useFrame((state) => {
    const t = state.clock.getElapsedTime();

    if (meshRef.current) {
      meshRef.current.rotation.y += 0.004;
    }

    brainMaterials.forEach((material, index) => {
      material.emissiveIntensity = 0.65 + Math.sin(t * 2.2 + index * 0.12) * 0.35;
      material.opacity = 0.16 + Math.sin(t * 1.6 + index * 0.07) * 0.05;
    });
  });

  useEffect(() => {
    return () => {
      brainMaterials.forEach((material) => material.dispose());
    };
  }, [brainMaterials]);

  const getCircuitColor = (index: number) => {
    const palette = [0x4df5ff, 0x8dfff1, 0x5ca9ff, 0xa8ffcf];
    return palette[index % palette.length];
  };

  return (
    <group ref={meshRef}>
      {/* GLTF Brain Model from holo.glb */}
      <primitive object={brainModel} scale={[4, 4, 4]} />

      {/* Circuit pathways across brain wireframe */}
      {circuitPaths.map((path, index) => (
        <group key={`circuit-${index}`}>
          <line>
            <bufferGeometry>
              <bufferAttribute attach="attributes-position" args={[path.positions, 3]} />
            </bufferGeometry>
            <lineBasicMaterial color={getCircuitColor(index)} transparent opacity={0.24} />
          </line>
        </group>
      ))}
    </group>
  );
}

function DataOverlay({ momentsData, connectionStatus }: { momentsData: MomentData[], connectionStatus: string }) {
  return (
    <div className={styles.dataOverlay}>
      {/* Header */}
      <div className={styles.overlayHeader}>
        <div className={styles.overlayTitle}>Heart of the Grid</div>
        <div className={styles.overlaySubtitle}>Neural Cognitive Substrate</div>
      </div>

      {/* Grid Coherence */}
      <div className={styles.coherenceSection}>
        <div className={styles.coherenceTitle}>Grid Coherence</div>
        <div className={styles.coherenceText}>Pulse drawn from OmniNeural resonance loop.</div>
      </div>

      {/* Neo4j Status */}
      <div className={styles.statusSection}>
        <div className={styles.statusHeader}>
          <div className={`${styles.statusIndicator} ${connectionStatus === 'connected' ? styles.statusConnected :
            connectionStatus === 'syncing' ? styles.statusSyncing : styles.statusError
            }`}></div>
          <div className={styles.statusTitle}>NEO4J COGNITIVE SUBSTRATE</div>
        </div>
        <div className={styles.statusDetails}>
          <div>Knowledge Constellation</div>
          <div className={styles.statusActive}>Resonance Tracking Active</div>
          <div>{connectionStatus === 'connected' ? 'Synced with Neo4j constellation...' : 'Establishing neural link...'}</div>
        </div>
      </div>

      {/* Metrics */}
      <div className={styles.metricsSection}>
        <div className={styles.metricRow}>
          <span className={styles.metricLabel}>Neural Nodes:</span>
          <span className={`${styles.metricValue} ${styles.metricNodes}`}>{momentsData.length.toLocaleString()}</span>
        </div>
        <div className={styles.metricRow}>
          <span className={styles.metricLabel}>Coherence:</span>
          <span className={`${styles.metricValue} ${styles.metricCoherence}`}>{Math.floor(Math.random() * 40 + 60)}%</span>
        </div>
        <div className={styles.metricRow}>
          <span className={styles.metricLabel}>Resonance:</span>
          <span className={`${styles.metricValue} ${styles.metricResonance}`}>{connectionStatus === 'connected' ? 'SYNCHRONIZED' : 'CALIBRATING'}</span>
        </div>
      </div>

      {/* Live activity stream */}
      <div className={styles.activitySection}>
        <div className={styles.activityTitle}>Neural Activity Stream:</div>
        <div className={styles.activityStream}>
          {momentsData.slice(-4).reverse().map((moment, i) => (
            <div key={moment.id} className={styles.activityItem}>
              → {moment.content.slice(0, 35)}...
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default function BrainVisualization() {
  const [momentsData, setMomentsData] = useState<MomentData[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'syncing' | 'error'>('connecting');

  // Fetch real-time data from Neo4j
  useEffect(() => {
    const fetchMoments = async () => {
      try {
        setConnectionStatus('connecting');
        const response = await fetch('/api/moments');
        const data = await response.json();

        if (response.ok && data.moments && data.moments.length > 0) {
          setConnectionStatus('connected');
          // Transform Neo4j data into brain visualization format
          const transformedMoments: MomentData[] = data.moments.map((moment: any, index: number) => {
            // Generate brain region positions (you can map these to actual brain regions)
            const angle = (index / data.moments.length) * Math.PI * 2;
            const radius = 1.5 + Math.sin(index * 0.1) * 0.5;
            const height = Math.sin(index * 0.2) * 0.8;

            return {
              id: moment.id || `moment-${index}`,
              content: moment.content || moment.text || 'Neural activity',
              timestamp: moment.timestamp || moment.created_at || new Date().toISOString(),
              position: [
                Math.cos(angle) * radius,
                height,
                Math.sin(angle) * radius
              ] as [number, number, number],
              intensity: Math.random() * 0.5 + 0.5,
              category: moment.category || ['consciousness', 'memory', 'emotion', 'thought'][Math.floor(Math.random() * 4)]
            };
          });

          setMomentsData(transformedMoments);
        } else {
          setConnectionStatus('syncing');
          // Fallback: Generate demo data for visualization
          console.log('Using demo data - Neo4j response:', data);
          const demoMoments: MomentData[] = Array.from({ length: 50 }, (_, i) => {
            const angle = (i / 50) * Math.PI * 2;
            const radius = 1.2 + Math.sin(i * 0.1) * 0.3;
            const height = Math.cos(i * 0.15) * 0.6;

            return {
              id: `demo-${i}`,
              content: `Neural pattern ${i + 1}`,
              timestamp: new Date().toISOString(),
              position: [
                Math.cos(angle) * radius,
                height,
                Math.sin(angle) * radius
              ] as [number, number, number],
              intensity: Math.random() * 0.7 + 0.3,
              category: ['consciousness', 'memory', 'emotion', 'thought'][i % 4]
            };
          });

          setMomentsData(demoMoments);
        }

        setIsLoading(false);
      } catch (err) {
        console.error('Error fetching moments:', err);
        setError('Failed to connect to neural grid');
        setConnectionStatus('error');
        setIsLoading(false);
      }
    };

    fetchMoments();

    // Real-time updates every 5 seconds
    const interval = setInterval(fetchMoments, 5000);
    return () => clearInterval(interval);
  }, []);

  if (isLoading) {
    return (
      <div className={styles.loadingContainer}>
        <div className="text-center">
          <div className={styles.loadingSpinner}></div>
          <div>INITIALIZING NEURAL GRID...</div>
        </div>
      </div>
    );
  }

  return (
    <>
      <Canvas
        camera={{ position: [0, 0, 6], fov: 60 }}
        style={{ width: '100vw', height: '100vh', background: 'transparent' }}
      >
        <ambientLight intensity={0.4} />
        <pointLight position={[5, 5, 5]} intensity={0.8} color={0x00ffff} />
        <pointLight position={[-5, -5, -5]} intensity={0.4} color={0xff0080} />
        <pointLight position={[0, 8, 0]} intensity={0.3} color={0x00ff88} />

        <Suspense fallback={<Html center>Loading Brain Model...</Html>}>
          <BrainMesh />
        </Suspense>

        <OrbitControls
          enablePan={true}
          enableZoom={true}
          enableRotate={true}
          autoRotate={false}
          maxDistance={10}
          minDistance={2}
        />

        {/* Info text in 3D space */}
        <Text
          position={[0, -2.5, 0]}
          fontSize={0.12}
          color="#00ffff"
          anchorX="center"
          anchorY="middle"
        >
          MoStar Cognitive Substrate - {momentsData.length} Neural Nodes
        </Text>

        {/* Grid title */}
        <Text
          position={[0, 2.8, 0]}
          fontSize={0.18}
          color="#00ffff"
          anchorX="center"
          anchorY="middle"
        >
          Heart of the Grid
        </Text>
      </Canvas>

      <DataOverlay momentsData={momentsData} connectionStatus={connectionStatus} />

      {error && (
        <div className={styles.errorNotification}>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-red-400 rounded-full"></div>
            <span>{error}</span>
          </div>
        </div>
      )}

      {/* Neural activity particles background */}
      <div className={styles.particleBackground}>
        {Array.from({ length: 20 }).map((_, i) => (
          <div
            key={i}
            className="absolute w-1 h-1 bg-cyan-400 rounded-full animate-pulse"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 2}s`,
              animationDuration: `${2 + Math.random() * 3}s`
            }}
          />
        ))}
      </div>
    </>
  );
}

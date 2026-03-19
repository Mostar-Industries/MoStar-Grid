'use client';

import { Html, OrbitControls, Text, useGLTF } from '@react-three/drei';
import { Canvas, useFrame } from '@react-three/fiber';
import { Suspense, useEffect, useRef, useState } from 'react';
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

interface BrainMeshProps {
  momentsData: MomentData[];
}

function BrainMesh({ momentsData }: BrainMeshProps) {
  const meshRef = useRef<THREE.Group>(null);

  // Load the holo.glb brain model
  const { scene } = useGLTF('/holo.glb');

  useFrame(() => {
    if (meshRef.current) {
      meshRef.current.rotation.y += 0.002;
    }
  });

  // Clone and configure the brain model
  const brainModel = scene.clone();
  brainModel.traverse((child) => {
    if (child instanceof THREE.Mesh) {
      child.material = new THREE.MeshPhongMaterial({
        color: 0x00ffff,
        transparent: true,
        opacity: 0.2,
        wireframe: false,
        side: THREE.DoubleSide,
        emissive: 0x002244,
        emissiveIntensity: 0.3,
      });
    }
  });

  return (
    <group ref={meshRef}>
      {/* GLTF Brain Model from holo.glb */}
      <primitive object={brainModel} scale={[5, 5, 5,]} />

      {/* Neural Activity Points */}
      {momentsData.map((moment, index) => (
        <group key={moment.id} position={moment.position}>
          {/* Pulsing sphere for each moment */}
          <mesh>
            <sphereGeometry args={[0.05 + moment.intensity * 0.1, 16, 16]} />
            <meshBasicMaterial
              color={moment.category === 'consciousness' ? 0xff0080 :
                moment.category === 'memory' ? 0x00ff80 :
                  moment.category === 'emotion' ? 0xff8000 : 0x0080ff}
              transparent
              opacity={0.7 + Math.sin(Date.now() * 0.01 + index) * 0.3}
            />
          </mesh>

          {/* Data visualization trails */}
          <mesh position={[0, 0, 0]}>
            <cylinderGeometry args={[0.002, 0.002, moment.intensity, 8]} />
            <meshBasicMaterial
              color={0x00ffff}
              transparent
              opacity={0.5}
            />
          </mesh>
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
          <BrainMesh momentsData={momentsData} />
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

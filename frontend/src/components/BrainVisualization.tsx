'use client';

import React, { useRef, useState, useEffect, Suspense } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Html, Text } from '@react-three/drei';
import * as THREE from 'three';

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

  useFrame(() => {
    if (meshRef.current) {
      meshRef.current.rotation.y += 0.002;
    }
  });

  return (
    <group ref={meshRef}>
      {/* Main brain structure - transparent holographic mesh */}
      <mesh>
        <sphereGeometry args={[1.5, 64, 64]} />
        <meshPhongMaterial
          color={0x00ffff}
          transparent
          opacity={0.15}
          wireframe={false}
          side={THREE.DoubleSide}
          emissive={0x002244}
          emissiveIntensity={0.3}
        />
      </mesh>
      
      {/* Wireframe overlay for brain structure */}
      <mesh>
        <sphereGeometry args={[1.52, 32, 32]} />
        <meshBasicMaterial
          color={0x00aaff}
          transparent
          opacity={0.1}
          wireframe
        />
      </mesh>
      
      {/* Inner core glow */}
      <mesh>
        <sphereGeometry args={[0.8, 32, 32]} />
        <meshBasicMaterial
          color={0x0066ff}
          transparent
          opacity={0.05}
        />
      </mesh>

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
    <div className="absolute top-6 left-6 bg-black/70 backdrop-blur-md rounded-xl p-6 text-cyan-400 font-mono text-sm border border-cyan-500/20">
      {/* Header */}
      <div className="border-b border-cyan-500/30 pb-3 mb-4">
        <div className="text-lg font-bold text-cyan-300">Heart of the Grid</div>
        <div className="text-xs text-gray-400">Neural Cognitive Substrate</div>
      </div>
      
      {/* Grid Coherence */}
      <div className="mb-4">
        <div className="text-cyan-300 text-sm mb-2">Grid Coherence</div>
        <div className="text-xs text-gray-300">Pulse drawn from OmniNeural resonance loop.</div>
      </div>
      
      {/* Neo4j Status */}
      <div className="mb-4">
        <div className="text-cyan-300 text-sm mb-2 flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full animate-pulse ${
            connectionStatus === 'connected' ? 'bg-green-400' : 
            connectionStatus === 'syncing' ? 'bg-yellow-400' : 'bg-red-400'
          }`}></div>
          NEO4J COGNITIVE SUBSTRATE
        </div>
        <div className="space-y-1 text-xs">
          <div>Knowledge Constellation</div>
          <div className="text-green-400">Resonance Tracking Active</div>
          <div className="text-gray-400">{connectionStatus === 'connected' ? 'Synced with Neo4j constellation...' : 'Establishing neural link...'}</div>
        </div>
      </div>
      
      {/* Metrics */}
      <div className="space-y-2 mb-4">
        <div className="flex justify-between">
          <span>Neural Nodes:</span>
          <span className="text-green-400">{momentsData.length.toLocaleString()}</span>
        </div>
        <div className="flex justify-between">
          <span>Coherence:</span>
          <span className="text-blue-400">{Math.floor(Math.random() * 40 + 60)}%</span>
        </div>
        <div className="flex justify-between">
          <span>Resonance:</span>
          <span className="text-purple-400">{connectionStatus === 'connected' ? 'SYNCHRONIZED' : 'CALIBRATING'}</span>
        </div>
      </div>
      
      {/* Live activity stream */}
      <div className="border-t border-cyan-500/30 pt-3">
        <div className="text-xs text-cyan-300 mb-2">NEURAL ACTIVITY STREAM:</div>
        <div className="space-y-1 max-h-24 overflow-hidden">
          {momentsData.slice(-4).reverse().map((moment, i) => (
            <div key={moment.id} className="text-xs opacity-80 truncate text-gray-300">
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
      <div className="w-full h-screen bg-black flex items-center justify-center text-cyan-400 font-mono">
        <div className="text-center">
          <div className="animate-spin w-8 h-8 border-2 border-cyan-400 border-t-transparent rounded-full mx-auto mb-4"></div>
          <div>INITIALIZING NEURAL GRID...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full h-screen bg-black relative">
      <Canvas
        camera={{ position: [0, 0, 4], fov: 75 }}
        style={{ background: 'linear-gradient(180deg, #001133 0%, #000011 50%, #000000 100%)' }}
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
        <div className="absolute bottom-4 right-4 bg-red-900/50 backdrop-blur-sm rounded-lg p-3 text-red-400 font-mono text-sm">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-red-400 rounded-full"></div>
            <span>{error}</span>
          </div>
        </div>
      )}
      
      {/* Neural activity particles background */}
      <div className="absolute inset-0 pointer-events-none">
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
    </div>
  );
}

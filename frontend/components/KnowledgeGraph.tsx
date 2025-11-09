import React, { useState, useEffect, useRef } from 'react';
import { neo4jService, GraphData as Neo4jGraphData } from '../services/neo4jService';

interface Node {
    id: string;
    label: string;
    type: string;
    size: number;
}

interface Link {
    source: string;
    target: string;
}

interface GraphData {
    nodes: Node[];
    links: Link[];
}

interface KnowledgeGraphProps {
    data?: GraphData;
    autoFetch?: boolean;
    maxNodes?: number;
}

const nodeColors: { [key: string]: string } = {
    core: '#f5a623', // accent - orange
    culture: '#4a90e2', // primary - blue
    ontology: '#50e3c2', // secondary - cyan
    agent: '#9061F9', // purple
    knowledge: '#34D399', // emerald green
    sanctuary: '#FF6B9D', // pink/rose - for safe spaces
    governance: '#FFD700', // gold - for leadership systems
    medicine: '#7FFF00', // chartreuse - for healing
    principle: '#87CEEB', // sky blue - for concepts
};

const KnowledgeGraph: React.FC<KnowledgeGraphProps> = ({ data: externalData, autoFetch = true, maxNodes = 100 }) => {
    const containerRef = useRef<HTMLDivElement>(null);
    const [positions, setPositions] = useState<{ [key: string]: { x: number; y: number } }>({});
    const [dimensions, setDimensions] = useState({ width: 0, height: 0 });
    const [graphData, setGraphData] = useState<GraphData>(externalData || { nodes: [], links: [] });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [isConnected, setIsConnected] = useState(false);
    const [query, setQuery] = useState('MATCH (n) RETURN n LIMIT 50');

    // Check Neo4j connection on mount
    useEffect(() => {
        const checkConnection = async () => {
            if (neo4jService.isConfigured()) {
                try {
                    const connected = await neo4jService.testConnection();
                    setIsConnected(connected);
                    if (connected && autoFetch && !externalData) {
                        fetchGraphData();
                    }
                } catch (err) {
                    console.error('Neo4j connection test failed:', err);
                    setIsConnected(false);
                }
            }
        };
        checkConnection();
    }, [autoFetch, externalData]);

    // Update graph data when external data changes
    useEffect(() => {
        if (externalData) {
            setGraphData(externalData);
        }
    }, [externalData]);

    useEffect(() => {
        const updateDimensions = () => {
            if (containerRef.current) {
                setDimensions({
                    width: containerRef.current.offsetWidth,
                    height: containerRef.current.offsetHeight,
                });
            }
        };
        updateDimensions();
        window.addEventListener('resize', updateDimensions);
        return () => window.removeEventListener('resize', updateDimensions);
    }, []);

    // Fetch graph data from Neo4j
    const fetchGraphData = async () => {
        setLoading(true);
        setError(null);
        try {
            const neo4jData = await neo4jService.getGraphData(maxNodes);
            
            // Transform Neo4j data to component format
            const transformedData: GraphData = {
                nodes: neo4jData.nodes.map(node => ({
                    id: node.id,
                    label: node.properties.name || node.properties.title || node.label,
                    type: node.label.toLowerCase(),
                    size: 15
                })),
                links: neo4jData.relationships.map(rel => ({
                    source: rel.source,
                    target: rel.target
                }))
            };
            
            setGraphData(transformedData);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to fetch graph data');
            console.error('Error fetching graph data:', err);
        } finally {
            setLoading(false);
        }
    };

    // Execute custom Cypher query
    const executeQuery = async () => {
        setLoading(true);
        setError(null);
        try {
            const result = await neo4jService.query(query);
            
            // Transform query result to graph data
            const nodes: Node[] = [];
            const links: Link[] = [];
            const nodeIds = new Set<string>();

            result.records?.forEach((record: any) => {
                Object.values(record).forEach((value: any) => {
                    if (value && value.labels) {
                        // It's a node
                        const nodeId = value.identity?.toString() || value.id?.toString();
                        if (nodeId && !nodeIds.has(nodeId)) {
                            nodeIds.add(nodeId);
                            nodes.push({
                                id: nodeId,
                                label: value.properties?.name || value.properties?.title || value.labels[0],
                                type: value.labels[0]?.toLowerCase() || 'node',
                                size: 15
                            });
                        }
                    }
                });
            });

            setGraphData({ nodes, links });
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Query execution failed');
            console.error('Query error:', err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (dimensions.width > 0 && dimensions.height > 0) {
            // Initialize positions randomly
            const initialPositions: { [key: string]: { x: number; y: number; vx: number; vy: number } } = {};
            graphData.nodes.forEach(node => {
                initialPositions[node.id] = {
                    x: dimensions.width / 2 + (Math.random() - 0.5) * 100,
                    y: dimensions.height / 2 + (Math.random() - 0.5) * 100,
                    vx: 0,
                    vy: 0
                };
            });

            const simulation = () => {
                const newPositions = { ...initialPositions };

                // Simulation parameters
                const repulsionForce = 40;
                const linkForce = 0.05;
                const centerForce = 0.005;
                const damping = 0.95;

                for (let i = 0; i < 60; i++) { // Run simulation for a number of ticks
                    // Repulsion between nodes
                    graphData.nodes.forEach(nodeA => {
                        graphData.nodes.forEach(nodeB => {
                            if (nodeA.id === nodeB.id) return;
                            const dx = newPositions[nodeB.id].x - newPositions[nodeA.id].x;
                            const dy = newPositions[nodeB.id].y - newPositions[nodeA.id].y;
                            const distance = Math.sqrt(dx * dx + dy * dy) || 1;
                            const force = repulsionForce / (distance * distance);
                            const fx = (dx / distance) * force;
                            const fy = (dy / distance) * force;

                            newPositions[nodeA.id].vx -= fx;
                            newPositions[nodeA.id].vy -= fy;
                            newPositions[nodeB.id].vx += fx;
                            newPositions[nodeB.id].vy += fy;
                        });
                    });

                    // Attraction along links
                    graphData.links.forEach(link => {
                        const sourceNode = newPositions[link.source];
                        const targetNode = newPositions[link.target];
                        const dx = targetNode.x - sourceNode.x;
                        const dy = targetNode.y - sourceNode.y;
                        
                        sourceNode.vx += dx * linkForce;
                        sourceNode.vy += dy * linkForce;
                        targetNode.vx -= dx * linkForce;
                        targetNode.vy -= dy * linkForce;
                    });

                    // Centering force
                    graphData.nodes.forEach(node => {
                        const dx = dimensions.width / 2 - newPositions[node.id].x;
                        const dy = dimensions.height / 2 - newPositions[node.id].y;
                        newPositions[node.id].vx += dx * centerForce;
                        newPositions[node.id].vy += dy * centerForce;
                    });


                    // Update positions
                    graphData.nodes.forEach(node => {
                        const pos = newPositions[node.id];
                        pos.vx *= damping;
                        pos.vy *= damping;
                        pos.x += pos.vx;
                        pos.y += pos.vy;

                        // Boundary check
                        pos.x = Math.max(node.size, Math.min(dimensions.width - node.size, pos.x));
                        pos.y = Math.max(node.size, Math.min(dimensions.height - node.size, pos.y));
                    });
                }
                
                const finalPositions: { [key: string]: { x: number; y: number } } = {};
                Object.keys(newPositions).forEach(id => {
                    finalPositions[id] = { x: newPositions[id].x, y: newPositions[id].y };
                });

                setPositions(finalPositions);
            };

            simulation();
        }
    }, [graphData, dimensions.width, dimensions.height]);

    if (dimensions.width === 0) {
        return <div ref={containerRef} className="w-full h-full" />;
    }

    return (
        <div ref={containerRef} className="w-full h-full flex flex-col">
            {/* Neo4j Controls */}
            {!externalData && (
                <div className="p-4 bg-gray-900/50 backdrop-blur-sm border-b border-gray-700">
                    <div className="flex items-center gap-4 mb-2">
                        <div className="flex items-center gap-2">
                            <div className={`w-2 h-2 rounded-full ${
                                isConnected ? 'bg-green-500' : 'bg-red-500'
                            }`} />
                            <span className="text-sm text-gray-300">
                                {isConnected ? 'Neo4j Connected' : 'Neo4j Disconnected'}
                            </span>
                        </div>
                        <button
                            onClick={fetchGraphData}
                            disabled={loading || !isConnected}
                            className="px-3 py-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded text-sm text-white transition-colors"
                        >
                            {loading ? 'Loading...' : 'Refresh Graph'}
                        </button>
                        <span className="text-sm text-gray-400">
                            {graphData.nodes.length} nodes, {graphData.links.length} relationships
                        </span>
                    </div>
                    
                    {/* Query Input */}
                    <div className="flex gap-2">
                        <input
                            type="text"
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            placeholder="Enter Cypher query..."
                            className="flex-1 px-3 py-1 bg-gray-800 border border-gray-700 rounded text-sm text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
                            disabled={loading || !isConnected}
                        />
                        <button
                            onClick={executeQuery}
                            disabled={loading || !isConnected || !query}
                            className="px-4 py-1 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded text-sm text-white transition-colors"
                        >
                            Execute
                        </button>
                    </div>
                    
                    {error && (
                        <div className="mt-2 p-2 bg-red-900/30 border border-red-700 rounded text-sm text-red-300">
                            {error}
                        </div>
                    )}
                </div>
            )}
            
            {/* Graph Visualization */}
            <div className="flex-1 relative">
                {loading && (
                    <div className="absolute inset-0 flex items-center justify-center bg-gray-900/50 backdrop-blur-sm z-10">
                        <div className="text-white text-lg">Loading graph data...</div>
                    </div>
                )}
                
                {graphData.nodes.length === 0 && !loading && (
                    <div className="absolute inset-0 flex items-center justify-center text-gray-400">
                        <div className="text-center">
                            <p className="text-lg mb-2">No graph data available</p>
                            {isConnected && (
                                <button
                                    onClick={fetchGraphData}
                                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded text-white transition-colors"
                                >
                                    Load Graph Data
                                </button>
                            )}
                        </div>
                    </div>
                )}
                
                <svg width={dimensions.width} height={dimensions.height}>
                <defs>
                    {Object.entries(nodeColors).map(([key, color]) => (
                        <radialGradient key={key} id={`grad-${key}`}>
                            <stop offset="0%" stopColor={color} stopOpacity="1" />
                            <stop offset="100%" stopColor={color} stopOpacity="0.2" />
                        </radialGradient>
                    ))}
                </defs>
                
                    {/* Render Links */}
                    {graphData.links.map((link, i) => {
                    const sourcePos = positions[link.source];
                    const targetPos = positions[link.target];
                    if (!sourcePos || !targetPos) return null;
                    return (
                        <line
                            key={i}
                            x1={sourcePos.x}
                            y1={sourcePos.y}
                            x2={targetPos.x}
                            y2={targetPos.y}
                            className="graph-link"
                        />
                    );
                })}

                    {/* Render Nodes */}
                    {graphData.nodes.map(node => {
                    const pos = positions[node.id];
                    if (!pos) return null;
                    const color = nodeColors[node.type] || '#ccc';
                    return (
                        <g key={node.id} transform={`translate(${pos.x}, ${pos.y})`} className="graph-node">
                            <circle
                                r={node.size}
                                fill={`url(#grad-${node.type})`}
                                stroke={color}
                                strokeWidth="2"
                            />
                            {node.type === 'core' && (
                               <circle
                                r={node.size}
                                fill="transparent"
                                stroke={color}
                                strokeWidth="2"
                                style={{
                                    animation: 'node-pulse 2s infinite ease-out',
                                    '--start-radius': `${node.size}px`,
                                    '--end-radius': `${node.size * 2}px`,
                                } as React.CSSProperties}
                                />
                            )}
                            <text
                                y={node.size + 8} // Position below the node
                                className="graph-text"
                            >
                                {node.label}
                            </text>
                        </g>
                    );
                })}
                </svg>
            </div>
        </div>
    );
};

export default KnowledgeGraph;

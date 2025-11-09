import React, { useState, useCallback } from 'react';
import Button from './Button';
import Input from './Input';
import LoadingSpinner from './LoadingSpinner';
import * as backendService from '../services/backendService';
import { MostarGridQueryResponse, KnowledgeNodeResponse, CAREAccessResponse, GridStatusResponse } from '../types';

const BackendAlignmentPage: React.FC = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<KnowledgeNodeResponse[] | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [careAccessNodeId, setCareAccessNodeId] = useState('');
  const [careAccessResult, setCareAccessResult] = useState<CAREAccessResponse | null>(null);
  const [stats, setStats] = useState<GridStatusResponse | null>(null);
  const [culturalContext, setCulturalContext] = useState('Yoruba'); // Default context

  const handleQuerySubmit = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    setResults(null);
    try {
      const response: MostarGridQueryResponse = await backendService.queryMostarGrid({ 
        query, 
        culture: culturalContext,
        limit: 5 // Limit to 5 results for cleaner display
      });
      setResults(response.nodes);
    } catch (err: any) {
      setError(err.message || 'Failed to query Mostar GRID.');
    } finally {
      setIsLoading(false);
    }
  }, [query, culturalContext]);

  const handleCareAccessSubmit = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    setCareAccessResult(null);
    try {
      const response: CAREAccessResponse = await backendService.validateCareAccess({ 
        node_id: careAccessNodeId, 
      });
      setCareAccessResult(response);
    } catch (err: any) {
      setError(err.message || 'Failed to validate CARE access. Ensure Node ID is correct and valid.');
    } finally {
      setIsLoading(false);
    }
  }, [careAccessNodeId]);

  const fetchStatistics = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    setStats(null);
    try {
      const response: GridStatusResponse = await backendService.getMostarGridStatistics();
      setStats(response);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch GRID statistics.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  return (
    <div className="flex flex-col p-4 md:p-8 max-w-4xl mx-auto bg-card rounded-lg shadow-custom space-y-8 text-textPrimary">
      <h2 className="text-3xl font-bold text-center text-primary mb-6">Backend Alignment: MoStar GRID Core</h2>

      {/* Main Query Section */}
      <div className="grid-card rounded-lg shadow p-6">
        <h3 className="text-2xl font-semibold text-textPrimary mb-4">Query Cultural Knowledge</h3>
        <div className="flex flex-col md:flex-row gap-4 mb-4">
          <Input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g., safe medicinal herbs for menstrual pain"
            className="flex-grow p-3 border rounded-md"
            label="Knowledge Query"
          />
          <Input
            type="text"
            value={culturalContext}
            onChange={(e) => setCulturalContext(e.target.value)}
            placeholder="e.g., Yoruba, Swahili"
            className="w-full md:w-48 p-3 border rounded-md"
            label="Cultural Context"
          />
        </div>
        <Button onClick={handleQuerySubmit} isLoading={isLoading} className="w-full md:w-auto">
          Query Knowledge Fabric
        </Button>

        {isLoading && <LoadingSpinner />}
        {error && <p className="text-red-500 mt-4">{error}</p>}

        {results && (
          <div className="mt-6 p-4 bg-background rounded-md border border-border text-textPrimary">
            <h4 className="text-xl font-semibold mb-3">Knowledge Nodes ({results.length})</h4>
            {results.length > 0 ? (
              <ul className="list-disc pl-5 space-y-3">
                {results.map((node, index) => (
                  <li key={node.node_id || index} className="bg-white p-3 rounded-md shadow-sm border border-gray-200">
                    {/* FIX: Explicitly cast to string for rendering to avoid 'unknown' type error if it somehow occurs,
                            though with correct types.ts, `node.content.remedy` should be `string | undefined`. */}
                    <p className="font-bold text-lg text-primary">{node.content.remedy || 'Unnamed Node'}</p>
                    <p><strong>Node ID:</strong> <span className="text-sm text-gray-600 break-all">{node.node_id}</span></p>
                    <p><strong>Culture:</strong> {node.culture}</p>
                    <p><strong>Ontology:</strong> {node.ontology}</p>
                    <p><strong>Uses:</strong> {node.content.uses || 'N/A'}</p>
                    <p><strong>Safety:</strong> <span className={`font-semibold ${node.content.safety_level === 'High' ? 'text-green-600' : node.content.safety_level === 'Moderate' ? 'text-yellow-600' : 'text-red-600'}`}>{node.content.safety_level || 'N/A'}</span></p>
                    <p><strong>Source Provenance:</strong> {node.provenance.join(', ') || 'N/A'}</p>
                    <p><strong>Confidence:</strong> {node.confidence?.toFixed(2)}</p>
                    <p className="mt-2 text-sm"><strong>CARE Metadata:</strong>
                      <ul className="list-disc pl-4 text-gray-700">
                        <li><strong>FPIC Obtained:</strong> {node.care_metadata.fpic_obtained ? '✅ Yes' : '❌ No'}</li>
                        <li><strong>Permission:</strong> {node.care_metadata.permission_level}</li>
                        <li><strong>Community:</strong> {node.care_metadata.community}</li>
                        <li><strong>Governance:</strong> {node.care_metadata.governance_protocol}</li>
                      </ul>
                    </p>
                  </li>
                ))}
              </ul>
            ) : (
              <p>No knowledge nodes found for your query.</p>
            )}
          </div>
        )}
      </div>

      {/* CARE Access Validation Section */}
      <div className="grid-card rounded-lg shadow p-6">
        <h3 className="text-2xl font-semibold text-textPrimary mb-4">CARE Access Validation</h3>
        <Input
          type="text"
          value={careAccessNodeId}
          onChange={(e) => setCareAccessNodeId(e.target.value)}
          placeholder="Enter Knowledge Node ID (e.g., d4e9e4f5-a1b2-c3d4-e5f6-1234567890ab)"
          className="mb-4 p-3 border rounded-md w-full font-mono text-sm"
          label="Knowledge Node ID"
        />
        <Button onClick={handleCareAccessSubmit} isLoading={isLoading} className="w-full md:w-auto">
          Validate CARE Access
        </Button>

        {careAccessResult && (
          <div className="mt-4 p-4 bg-background rounded-md border border-border text-textPrimary">
            <h4 className="text-xl font-semibold mb-3">Access Validation for Node "{careAccessResult.node_id}"</h4>
            <p className={`font-bold text-lg ${careAccessResult.compliant ? 'text-green-600' : 'text-red-600'}`}>
              {careAccessResult.compliant ? '✅ Access Compliant' : '❌ Access Non-Compliant'}
            </p>
            <p><strong>Reason:</strong> {careAccessResult.compliant ? 'Access granted based on CARE principles.' : 'Access denied due to CARE principle violation or missing information.'}</p>
            <p><strong>FPIC Obtained:</strong> {careAccessResult.fpic_obtained ? '✅ Yes' : '❌ No'}!</p>
            <p><strong>Permission Level:</strong> {careAccessResult.permission_level}</p>
            <p><strong>Community:</strong> {careAccessResult.community}</p>
            <p><strong>Governance Protocol:</strong> {careAccessResult.governance_protocol}</p>
          </div>
        )}
      </div>

      {/* Statistics Section */}
      <div className="grid-card rounded-lg shadow p-6">
        <h3 className="text-2xl font-semibold text-textPrimary mb-4">GRID Consciousness Status</h3>
        <Button onClick={fetchStatistics} isLoading={isLoading} className="w-full md:w-auto mb-4">
          Fetch GRID Status
        </Button>
        {stats && (
          <div className="mt-4 p-4 bg-background rounded-md border border-border text-textPrimary grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
                <h5 className="font-semibold text-lg text-primary mb-2">Consciousness Layer</h5>
                <p><strong>Grid ID:</strong> <span className="text-sm break-all">{stats.consciousness.grid_id}</span></p>
                <p><strong>Level:</strong> {stats.consciousness.consciousness_level}</p>
                <p><strong>Connected Agents:</strong> {stats.consciousness.connected_agents}</p>
                <p><strong>Active Agents:</strong> {stats.consciousness.active_agents}</p>
                <p><strong>Cultures Represented:</strong> {stats.consciousness.cultures_represented}</p>
                <p><strong>Uptime (seconds):</strong> {stats.consciousness.uptime_seconds}</p>
            </div>
            <div>
                <h5 className="font-semibold text-lg text-primary mb-2">Knowledge Fabric</h5>
                <p><strong>Total Nodes:</strong> {stats.knowledge_fabric.total_nodes}</p>
                <p><strong>Total Cultures:</strong> {stats.knowledge_fabric.cultures}</p>
                <p><strong>Total Ontologies:</strong> {stats.knowledge_fabric.ontologies}</p>
                <p><strong>CARE Compliant:</strong> {stats.knowledge_fabric.care_compliant_percentage}%</p>
                <p><strong>Recent Contributions:</strong> {stats.knowledge_fabric.recent_contributions}</p>
            </div>
            <div>
                <h5 className="font-semibold text-lg text-primary mb-2">Agent Registry</h5>
                <p><strong>Total Agents:</strong> {stats.agents.total}</p>
                <p><strong>Active Agents:</strong> {stats.agents.active}</p>
                <p className="mt-2 font-medium">Agents by Type:</p>
                <ul className="list-disc pl-5 text-sm">
                    {Object.entries(stats.agents.by_type).map(([type, count]) => (
                        <li key={type}>{type.charAt(0).toUpperCase() + type.slice(1)}: {count}</li>
                    ))}
                </ul>
            </div>
            <div>
                <h5 className="font-semibold text-lg text-primary mb-2">Reasoning Chains</h5>
                <p><strong>Active Chains:</strong> {stats.reasoning_chains.active}</p>
                <p><strong>Completed Today:</strong> {stats.reasoning_chains.completed_today}</p>
                <p><strong>Total Chains:</strong> {stats.reasoning_chains.total}</p>
                <p className="mt-2 font-medium">Top Cultures in Knowledge Fabric:</p>
                <ul className="list-disc pl-5 text-sm">
                    {stats.knowledge_fabric.top_cultures.map((culture, index) => (
                        <li key={index}>{culture}</li>
                    ))}
                </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default BackendAlignmentPage;
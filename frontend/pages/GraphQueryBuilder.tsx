import React, { useState } from 'react';
import axios from 'axios';

interface QueryResult {
  records: any[];
  summary: {
    count: number;
  };
}

const GraphQueryBuilder: React.FC = () => {
  const [query, setQuery] = useState('MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 10');
  const [result, setResult] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [recordCount, setRecordCount] = useState(0);

  // Preset queries for quick access
  const presetQueries = [
    {
      name: 'All Nodes & Relationships',
      query: 'MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 25'
    },
    {
      name: 'Governance Systems',
      query: 'MATCH (n) WHERE n.type IN ["Monarchical", "Democratic", "Federal", "Consensual"] RETURN n LIMIT 20'
    },
    {
      name: 'Traditional Medicine',
      query: 'MATCH (n) WHERE n.uses IS NOT NULL RETURN n.name AS medicine, n.uses AS uses, n.owner AS owner LIMIT 15'
    },
    {
      name: 'Oba Kingship Connections',
      query: 'MATCH (oba {name: "Oba Kingship"})-[r]->(m) RETURN oba, type(r) AS relationship, m.name AS connected_to LIMIT 20'
    },
    {
      name: 'All Node Types',
      query: 'MATCH (n) RETURN DISTINCT labels(n) AS node_types, count(n) AS count'
    },
    {
      name: 'Relationship Types',
      query: 'MATCH ()-[r]->() RETURN DISTINCT type(r) AS relationship_type, count(r) AS count ORDER BY count DESC'
    }
  ];

  const runQuery = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setError('');
    setResult('');

    try {
      const res = await axios.post<QueryResult>('http://localhost:7000/api/neo4j/query', {
        cypher: query,
        parameters: {}
      });

      setResult(JSON.stringify(res.data, null, 2));
      setRecordCount(res.data.records?.length || 0);
    } catch (e: any) {
      const errorMsg = e.response?.data?.detail || e.message;
      setError(`Query failed: ${errorMsg}`);
      setResult('');
    } finally {
      setLoading(false);
    }
  };

  const loadPreset = (presetQuery: string) => {
    setQuery(presetQuery);
    setError('');
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && e.ctrlKey) {
      runQuery();
    }
  };

  return (
    <div className="flex flex-col h-full p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-white flex items-center gap-3">
            <span className="text-4xl">🧠</span>
            Query the Mind of the Grid
          </h2>
          <p className="text-gray-400 mt-1">
            Direct Cypher access to the Neo4j knowledge graph
          </p>
        </div>
        {recordCount > 0 && (
          <div className="px-3 py-1 bg-purple-900/30 border border-purple-700 rounded-lg text-purple-400 text-sm">
            {recordCount} records returned
          </div>
        )}
      </div>

      {/* Preset Queries */}
      <div className="space-y-2">
        <label className="text-sm font-semibold text-gray-300">Quick Queries:</label>
        <div className="flex flex-wrap gap-2">
          {presetQueries.map((preset, index) => (
            <button
              key={index}
              onClick={() => loadPreset(preset.query)}
              className="px-3 py-1.5 bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-lg text-sm text-gray-300 transition-colors"
            >
              {preset.name}
            </button>
          ))}
        </div>
      </div>

      {/* Query Input */}
      <div className="space-y-3">
        <label className="text-sm font-semibold text-gray-300">Cypher Query:</label>
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={handleKeyPress}
          rows={6}
          className="w-full p-4 border border-gray-700 rounded-lg bg-gray-900 text-green-400 font-mono text-sm placeholder-gray-600 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
          placeholder="MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 10"
          disabled={loading}
        />
        
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-500">
            Ctrl+Enter to execute
          </span>
          <button
            onClick={runQuery}
            disabled={loading || !query.trim()}
            className="px-6 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-semibold rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {loading ? (
              <>
                <i className="fas fa-spinner fa-spin"></i>
                Executing...
              </>
            ) : (
              <>
                <i className="fas fa-play"></i>
                Run Query
              </>
            )}
          </button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="p-4 bg-red-900/30 border border-red-700 rounded-lg text-red-300">
          <i className="fas fa-exclamation-triangle mr-2"></i>
          {error}
        </div>
      )}

      {/* Results Display */}
      {result && (
        <div className="flex-1 overflow-hidden flex flex-col">
          <div className="flex items-center justify-between mb-2">
            <label className="text-sm font-semibold text-gray-300">Results:</label>
            <button
              onClick={() => navigator.clipboard.writeText(result)}
              className="px-3 py-1 text-xs bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded text-gray-400 hover:text-gray-300 transition-colors"
            >
              <i className="fas fa-copy mr-1"></i>
              Copy JSON
            </button>
          </div>
          <pre className="flex-1 bg-black text-green-400 p-4 rounded-lg text-xs overflow-auto font-mono border border-gray-800">
            {result}
          </pre>
        </div>
      )}

      {/* Empty State */}
      {!result && !loading && !error && (
        <div className="flex-1 flex items-center justify-center text-gray-500">
          <div className="text-center space-y-4">
            <div className="text-6xl">⚡</div>
            <p className="text-lg">Execute a Cypher query to see results</p>
            <div className="text-sm space-y-1 text-gray-600">
              <p>• Select a preset query above</p>
              <p>• Or write your own Cypher</p>
              <p>• Press Ctrl+Enter to run</p>
            </div>
          </div>
        </div>
      )}

      {/* Query Tips */}
      <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
        <h3 className="text-sm font-semibold text-gray-300 mb-2">💡 Query Tips:</h3>
        <ul className="text-xs text-gray-500 space-y-1">
          <li>• Use <code className="text-purple-400">LIMIT</code> to control result size</li>
          <li>• Filter by properties: <code className="text-purple-400">WHERE n.name = "Oba Kingship"</code></li>
          <li>• Get relationship types: <code className="text-purple-400">type(r)</code></li>
          <li>• Count results: <code className="text-purple-400">RETURN count(n)</code></li>
        </ul>
      </div>
    </div>
  );
};

export default GraphQueryBuilder;

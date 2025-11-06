import { useState, useEffect } from 'react';
import Head from 'next/head';

export default function Dashboard() {
  const [gridData, setGridData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [dbSource, setDbSource] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  useEffect(() => {
    // Fetch data from your API
    const fetchData = async () => {
      try {
        const response = await fetch('/api/grid-data');
        const result = await response.json();
        
        if (result.error) {
          console.error(result.error);
          setLoading(false);
          return;
        }
        
        setGridData(result.data);
        setDbSource(result.meta?.source);
        setLastUpdated(result.meta?.timestamp ? new Date(result.meta.timestamp) : new Date());
        setLoading(false);
      } catch (error) {
        console.error("Failed to fetch grid data:", error);
        setLoading(false);
      }
    };

    fetchData();
    
    // Set up polling for real-time updates
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="container">
      <Head>
        <title>MoStar Grid Dashboard</title>
      </Head>
      
      <h1>MoStar Grid Dashboard</h1>
      
      {dbSource && (
        <div className="db-status">
          <p>
            <strong>Database:</strong> 
            <span className={\db-badge \\}>
              {dbSource === 'local' ? 'Local PostgreSQL' : 'Neon Cloud'}
            </span>
          </p>
          {lastUpdated && (
            <p>
              <strong>Last updated:</strong> {lastUpdated.toLocaleTimeString()}
            </p>
          )}
        </div>
      )}
      
      {loading ? (
        <div className="loading">
          <p>Loading grid data...</p>
          <div className="spinner"></div>
        </div>
      ) : gridData ? (
        <div className="grid-container">
          <h2>Grid Status</h2>
          {Array.isArray(gridData) && gridData.length > 0 ? (
            <table className="grid-table">
              <thead>
                <tr>
                  {Object.keys(gridData[0]).map((key) => (
                    <th key={key}>{key}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {gridData.map((row, i) => (
                  <tr key={i}>
                    {Object.values(row).map((value, j) => (
                      <td key={j}>{JSON.stringify(value)}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="empty-state">
              <p>No grid data available</p>
            </div>
          )}
        </div>
      ) : (
        <div className="error-state">
          <p>Failed to load grid data</p>
          <button onClick={() => window.location.reload()}>Retry</button>
        </div>
      )}
    </div>
  );
}

// components/SystemStatus.tsx

import { useEffect, useState } from 'react';
import { getActiveDbType } from '../lib/db';
import { isRedisAvailable } from '../lib/cache';

const SystemStatus: React.FC = () => {
  const [dbType, setDbType] = useState<string>('neon');
  const [redisStatus, setRedisStatus] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    async function checkStatus() {
      try {
        // We know it's always neon now, but keeping the function call
        // in case we want to revert to dynamic checks later
        const dbStatus = await getActiveDbType();
        setDbType(dbStatus);
        
        const redisActive = await isRedisAvailable();
        setRedisStatus(redisActive);
      } catch (error) {
        console.error("Status check failed:", error);
      } finally {
        setLoading(false);
      }
    }
    
    checkStatus();
  }, []);

  if (loading) {
    return <div className="db-status loading">Checking system status...</div>;
  }

  return (
    <div className="db-status">
      <p>
        <strong>Database:</strong>
        <span className={`db-badge neon`}>Neon Cloud</span>
      </p>
      <p>
        <strong>Cache:</strong>
        <span className={`db-badge ${redisStatus ? 'neon' : 'local'}`}>
          {redisStatus ? 'Redis Active' : 'Redis Unavailable'}
        </span>
      </p>
    </div>
  );
};

export default SystemStatus;
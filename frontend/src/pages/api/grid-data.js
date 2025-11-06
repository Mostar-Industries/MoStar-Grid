import { executeQuery, getActiveDbType } from '../../lib/db';
import { getCachedOrSet } from '../../lib/cache';

export default async function handler(req, res) {
  try {
    // Use the cache utility with a 30-second TTL
    const gridData = await getCachedOrSet('grid_status', 30, async () => {
      // This function only runs on cache miss
      const result = await executeQuery('SELECT * FROM grid_status');
      return result.rows;
    });
    
    // Add metadata about which database was used
    const dbType = await getActiveDbType();
    
    res.status(200).json({
      data: gridData,
      meta: {
        source: dbType,
        timestamp: new Date().toISOString()
      }
    });
  } catch (err) {
    console.error('Grid DB error:', err);
    res.status(500).json({ 
      error: 'Grid service unavailable',
      message: err.message
    });
  }
}

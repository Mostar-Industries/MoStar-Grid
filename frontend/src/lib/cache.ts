import Redis from 'ioredis';

// Initialize Redis client
let redis;
try {
  redis = new Redis(process.env.REDIS_URL || 'redis://localhost:6379');
  
  redis.on('error', (err) => {
    console.warn('Redis connection error:', err);
    redis = null;
  });
  
  console.log('Redis client initialized');
} catch (error) {
  console.warn('Failed to initialize Redis:', error.message);
  redis = null;
}

/**
 * Get data from cache or fetch and store it
 * @param {string} key - Cache key
 * @param {number} ttlSeconds - Time to live in seconds
 * @param {Function} fetchFn - Async function to fetch data if not in cache
 * @returns {Promise<any>} - The requested data
 */
export async function getCachedOrSet(key, ttlSeconds, fetchFn) {
  // If Redis is not available, just fetch the data
  if (!redis) {
    return await fetchFn();
  }

  try {
    // Try to get from cache
    const cached = await redis.get(key);
    if (cached) {
      console.log('Cache hit for key:', key);
      return JSON.parse(cached);
    }

    // Cache miss, fetch data
    console.log('Cache miss for key:', key);
    const data = await fetchFn();
    
    // Store in cache
    await redis.set(key, JSON.stringify(data), 'EX', ttlSeconds);
    return data;
  } catch (error) {
    console.error('Cache error:', error);
    // Fallback to direct fetch if cache operation fails
    return await fetchFn();
  }
}

/**
 * Invalidate a cache key
 * @param {string} key - Cache key to invalidate
 */
export async function invalidateCache(key) {
  if (!redis) return;
  
  try {
    await redis.del(key);
    console.log(`Invalidated cache for key=${key}`);
  } catch (error) {
    console.error('Failed to invalidate cache:', error);
  }
}

/**
 * Check if Redis is available
 * @returns {boolean} - True if Redis is connected
 */
export function isRedisAvailable() {
  return redis !== null && redis.status === 'ready';
}

// lib/cache.js - Add this function

export async function isRedisAvailable(): Promise<boolean> {
  try {
    const redis = new Redis('redis://localhost:6379');
    await redis.ping();
    await redis.quit();
    return true;
  } catch (error) {
    console.error("Redis connection error:", error);
    return false;
  }
}
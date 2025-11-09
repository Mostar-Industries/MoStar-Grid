import { BACKEND_API_BASE_URL } from '../constants';
import { MostarGridQueryResponse, GridStatusResponse, CAREAccessResponse, KnowledgeNodeResponse } from '../types';

interface KnowledgeQueryRequest {
  query: string;
  culture?: string;
  ontology?: string;
  limit?: number;
}

interface CAREAccessRequest {
  node_id: string;
}

export async function queryMostarGrid(
  request: KnowledgeQueryRequest
): Promise<MostarGridQueryResponse> {
  try {
    const params = new URLSearchParams();
    if (request.query) params.append('query', request.query);
    if (request.culture) params.append('culture', request.culture);
    if (request.ontology) params.append('ontology', request.ontology);
    if (request.limit) params.append('limit', request.limit.toString());

    const response = await fetch(`${BACKEND_API_BASE_URL}/grid/knowledge/query?${params.toString()}`, {
      method: 'GET',
      headers: { 
        'Content-Type': 'application/json',
        // In a real scenario, you'd add Authorization headers here if needed by the backend
        // 'Authorization': `Bearer ${process.env.GRID_API_KEY}`, 
        // 'X-Agent-ID': 'frontend-browser-agent' 
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error querying Mostar GRID backend:', error);
    throw error;
  }
}

export async function getMostarGridStatistics(): Promise<GridStatusResponse> {
  try {
    const response = await fetch(`${BACKEND_API_BASE_URL}/grid/status`, {
      method: 'GET',
      headers: { 
        'Content-Type': 'application/json',
        // 'Authorization': `Bearer ${process.env.GRID_API_KEY}`, 
        // 'X-Agent-ID': 'frontend-browser-agent' 
      },
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching Mostar GRID statistics:', error);
    throw error;
  }
}

export async function validateCareAccess(
  request: CAREAccessRequest
): Promise<CAREAccessResponse> {
  try {
    const response = await fetch(`${BACKEND_API_BASE_URL}/grid/knowledge/${request.node_id}/care`, {
      method: 'GET',
      headers: { 
        'Content-Type': 'application/json',
        // 'Authorization': `Bearer ${process.env.GRID_API_KEY}`, 
        // 'X-Agent-ID': 'frontend-browser-agent' 
      },
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error validating CARE access:', error);
    throw error;
  }
}
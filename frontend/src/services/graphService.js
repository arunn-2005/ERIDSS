import api from "./api";

// 1. Sync graph data for a specific document to Neo4j
export const syncDocumentGraph = async (documentId) => {
  const response = await api.post(`/documents/${documentId}/sync`);
  return response.data;
};

// 2. Fetch critical high-risk nodes (bottlenecks) based on centrality scores
export const fetchCriticalRiskNodes = async (limit = 10) => {
  const response = await api.get(`/documents/risk-analysis/critical-nodes?limit=${limit}`);
  return response.data;
};
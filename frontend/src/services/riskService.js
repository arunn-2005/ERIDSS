import api from './api';

export const getCriticalNodes = async (limit = 10) => {
  const response = await api.get(`/risk-analysis/critical-nodes?limit=${limit}`);
  return response.data;
};

export const recalculateCentrality = async () => {
  const response = await api.post('/risk-analysis/recalculate');
  return response.data;
};

export const calculateCompositeScores = async () => {
  const response = await api.post('/risk-analysis/calculate-composite-scores');
  return response.data;
};

export const simulateFailure = async (nodeId, maxDepth = 4) => {
  const response = await api.post(`/risk-analysis/simulate-failure?node_id=${nodeId}&max_depth=${maxDepth}`);
  return response.data;
};

export const simulateMultiFailure = async (nodeIds, maxDepth = 4) => {
  const response = await api.post('/risk-analysis/simulate-multi-failure', {
    node_ids: nodeIds,
    max_depth: maxDepth
  });
  return response.data;
};

export const getMitigationRecommendations = async (limit = 5) => {
  const response = await api.get(`/risk-analysis/recommendations?limit=${limit}`);
  return response.data;
};
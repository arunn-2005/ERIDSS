import React, { useEffect, useState } from "react";
import { fetchCriticalRiskNodes } from "../services/graphService";

const RiskAnalysis = () => {
  const [criticalNodes, setCriticalNodes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadRiskData = async () => {
      try {
        setLoading(true);
        const data = await fetchCriticalRiskNodes(10);
        setCriticalNodes(data.critical_nodes || []);
      } catch (err) {
        console.error("Error loading risk metrics:", err);
        setError("Failed to retrieve topological risk metrics.");
      } finally {
        setLoading(false);
      }
    };

    loadRiskData();
  }, []);

  if (loading) {
    return <div className="p-6 text-gray-600 font-medium">Loading Risk Analysis Data...</div>;
  }

  if (error) {
    return <div className="p-6 text-red-600 font-medium">{error}</div>;
  }

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <h2 className="text-2xl font-bold mb-2 text-gray-800">
        Topological Risk & Single Points of Failure
      </h2>
      <p className="text-sm text-gray-600 mb-6">
        Identifies critical graph nodes ranked by Betweenness Centrality (Bridge Dependencies).
      </p>

      <div className="overflow-x-auto bg-white rounded-lg shadow border border-gray-200">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Entity Name</th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Type</th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Betweenness Risk</th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Degree Centrality</th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">In / Out Degree</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 bg-white">
            {criticalNodes.length === 0 ? (
              <tr>
                <td colSpan="5" className="px-6 py-6 text-center text-gray-500">
                  No risk metrics found. Sync a document to the Knowledge Graph first.
                </td>
              </tr>
            ) : (
              criticalNodes.map((node) => (
                <tr 
                  key={node.id} 
                  className={node.betweenness_centrality > 0.05 ? "bg-red-50 hover:bg-red-100" : "hover:bg-gray-50"}
                >
                  <td className="px-6 py-4 font-semibold text-gray-900">{node.name}</td>
                  <td className="px-6 py-4 text-gray-600">{node.type}</td>
                  <td className="px-6 py-4 text-red-600 font-bold">
                    {typeof node.betweenness_centrality === "number" ? node.betweenness_centrality.toFixed(4) : "0.0000"}
                  </td>
                  <td className="px-6 py-4 text-gray-700">
                    {typeof node.degree_centrality === "number" ? node.degree_centrality.toFixed(4) : "0.0000"}
                  </td>
                  <td className="px-6 py-4 text-gray-500 text-sm">
                    In: {node.in_degree} | Out: {node.out_degree}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default RiskAnalysis;
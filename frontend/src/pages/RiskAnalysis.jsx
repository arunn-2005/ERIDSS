import React, { useEffect, useState } from "react";
import { fetchCriticalRiskNodes } from "../services/graphService";
import "../styles/RiskAnalysis.css";
import {
  recalculateCentrality,
  calculateCompositeScores,
  simulateMultiFailure,
  getMitigationRecommendations,
} from "../services/riskService";

const RiskAnalysis = () => {
  const [activeTab, setActiveTab] = useState("overview");
  const [criticalNodes, setCriticalNodes] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [selectedNodeIds, setSelectedNodeIds] = useState([]);
  const [simulationResult, setSimulationResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [criticalData, recData] = await Promise.all([
        fetchCriticalRiskNodes(10),
        getMitigationRecommendations(5),
      ]);
      setCriticalNodes(criticalData.critical_nodes || []);
      setRecommendations(recData.mitigation_plans || []);
    } catch (err) {
      console.error("Error loading risk metrics:", err);
      setError("Failed to retrieve topological risk metrics.");
    } finally {
      setLoading(false);
    }
  };

  const handleRecalculateAll = async () => {
    try {
      setActionLoading(true);
      await recalculateCentrality();
      await calculateCompositeScores();
      await loadInitialData();
      alert("Risk metrics recalculated successfully!");
    } catch (err) {
      console.error("Failed to recalculate metrics:", err);
      alert("Error recalculating metrics.");
    } finally {
      setActionLoading(false);
    }
  };

  const handleNodeToggle = (id) => {
    setSelectedNodeIds((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  const handleRunSimulation = async () => {
    if (selectedNodeIds.length === 0) {
      alert("Please select at least one node to simulate failure.");
      return;
    }
    try {
      setActionLoading(true);
      const result = await simulateMultiFailure(selectedNodeIds, 4);
      setSimulationResult(result);
    } catch (err) {
      console.error("Simulation error:", err);
      alert("Failed to execute cascade simulation.");
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ padding: "24px", color: "#4b5563", fontWeight: "500" }}>
        Loading Risk Analysis Data...
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: "24px", color: "#dc2626", fontWeight: "500" }}>
        {error}
      </div>
    );
  }

  return (
    <div style={{ padding: "24px", maxWidth: "1200px", margin: "0 auto" }} className="space-y-6">
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
        <div>
          <h2 style={{ fontSize: "24px", fontWeight: "bold", color: "#1f2937", margin: 0 }}>
            Risk Intelligence & Decision Support
          </h2>
          <p style={{ fontSize: "14px", color: "#4b5563", margin: "4px 0 0 0" }}>
            Identifies critical graph nodes, simulates cascade outages, and provides mitigation plans.
          </p>
        </div>
        <button
          onClick={handleRecalculateAll}
          disabled={actionLoading}
          style={{
            backgroundColor: "#2563eb",
            color: "white",
            fontWeight: "600",
            padding: "8px 16px",
            borderRadius: "6px",
            border: "none",
            cursor: actionLoading ? "not-allowed" : "pointer",
            opacity: actionLoading ? 0.6 : 1,
          }}
        >
          {actionLoading ? "Processing..." : "Recalculate Metrics"}
        </button>
      </div>

      {/* Tabs */}
      <div style={{ display: "flex", borderBottom: "2px solid #e5e7eb", marginBottom: "20px" }}>
        <button
          onClick={() => setActiveTab("overview")}
          style={{
            padding: "10px 16px",
            fontWeight: "600",
            border: "none",
            background: "transparent",
            cursor: "pointer",
            color: activeTab === "overview" ? "#2563eb" : "#6b7280",
            borderBottom: activeTab === "overview" ? "2px solid #2563eb" : "2px solid transparent",
            marginBottom: "-2px",
          }}
        >
          Critical Entities
        </button>
        <button
          onClick={() => setActiveTab("simulator")}
          style={{
            padding: "10px 16px",
            fontWeight: "600",
            border: "none",
            background: "transparent",
            cursor: "pointer",
            color: activeTab === "simulator" ? "#2563eb" : "#6b7280",
            borderBottom: activeTab === "simulator" ? "2px solid #2563eb" : "2px solid transparent",
            marginBottom: "-2px",
          }}
        >
          Failure Simulator
        </button>
        <button
          onClick={() => setActiveTab("recommendations")}
          style={{
            padding: "10px 16px",
            fontWeight: "600",
            border: "none",
            background: "transparent",
            cursor: "pointer",
            color: activeTab === "recommendations" ? "#2563eb" : "#6b7280",
            borderBottom: activeTab === "recommendations" ? "2px solid #2563eb" : "2px solid transparent",
            marginBottom: "-2px",
          }}
        >
          Mitigation Plans
        </button>
      </div>

      {/* TAB 1: OVERVIEW */}
      {activeTab === "overview" && (
        <div style={{ backgroundColor: "#ffffff", borderRadius: "8px", border: "1px solid #e5e7eb", overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", textAlignment: "left" }}>
            <thead style={{ backgroundColor: "#f9fafb" }}>
              <tr>
                <th style={{ padding: "12px 16px", textAlign: "left", fontSize: "12px", color: "#6b7280", textTransform: "uppercase" }}>Entity Name</th>
                <th style={{ padding: "12px 16px", textAlign: "left", fontSize: "12px", color: "#6b7280", textTransform: "uppercase" }}>Type</th>
                <th style={{ padding: "12px 16px", textAlign: "left", fontSize: "12px", color: "#6b7280", textTransform: "uppercase" }}>Betweenness Risk</th>
                <th style={{ padding: "12px 16px", textAlign: "left", fontSize: "12px", color: "#6b7280", textTransform: "uppercase" }}>Degree Centrality</th>
                <th style={{ padding: "12px 16px", textAlign: "left", fontSize: "12px", color: "#6b7280", textTransform: "uppercase" }}>In / Out Degree</th>
              </tr>
            </thead>
            <tbody>
              {criticalNodes.length === 0 ? (
                <tr>
                  <td colSpan="5" style={{ padding: "24px", textAlign: "center", color: "#6b7280" }}>
                    No risk metrics found. Sync a document to the Knowledge Graph first.
                  </td>
                </tr>
              ) : (
                criticalNodes.map((node) => (
                  <tr
                    key={node.id}
                    style={{
                      borderTop: "1px solid #e5e7eb",
                      backgroundColor: node.betweenness_centrality > 0.05 ? "#fef2f2" : "#ffffff",
                    }}
                  >
                    <td style={{ padding: "14px 16px", fontWeight: "600", color: "#111827" }}>{node.name}</td>
                    <td style={{ padding: "14px 16px", color: "#4b5563" }}>{node.type}</td>
                    <td style={{ padding: "14px 16px", color: "#dc2626", fontWeight: "bold" }}>
                      {typeof node.betweenness_centrality === "number" ? node.betweenness_centrality.toFixed(4) : "0.0000"}
                    </td>
                    <td style={{ padding: "14px 16px", color: "#374151" }}>
                      {typeof node.degree_centrality === "number" ? node.degree_centrality.toFixed(4) : "0.0000"}
                    </td>
                    <td style={{ padding: "14px 16px", color: "#6b7280", fontSize: "14px" }}>
                      In: {node.in_degree} | Out: {node.out_degree}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* TAB 2: FAILURE SIMULATOR */}
      {activeTab === "simulator" && (
        <div style={{ backgroundColor: "#ffffff", padding: "24px", borderRadius: "8px", border: "1px solid #e5e7eb" }}>
          <div style={{ marginBottom: "16px" }}>
            <h3 style={{ fontSize: "18px", fontWeight: "bold", color: "#1f2937", margin: 0 }}>Multi-Node Outage Simulation</h3>
            <p style={{ fontSize: "14px", color: "#4b5563", margin: "4px 0 0 0" }}>Select candidate nodes to simulate simultaneous failure:</p>
          </div>

          <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", marginBottom: "20px" }}>
            {criticalNodes.map((node) => {
              const isSelected = selectedNodeIds.includes(node.id);
              return (
                <button
                  key={node.id}
                  onClick={() => handleNodeToggle(node.id)}
                  style={{
                    padding: "6px 14px",
                    borderRadius: "20px",
                    fontSize: "14px",
                    fontWeight: "500",
                    border: isSelected ? "1px solid #2563eb" : "1px solid #d1d5db",
                    backgroundColor: isSelected ? "#dbeafe" : "#f9fafb",
                    color: isSelected ? "#1e40af" : "#374151",
                    cursor: "pointer",
                  }}
                >
                  {isSelected ? "✓ " : "+ "}{node.name}
                </button>
              );
            })}
          </div>

          <button
            onClick={handleRunSimulation}
            disabled={actionLoading || selectedNodeIds.length === 0}
            style={{
              backgroundColor: "#111827",
              color: "white",
              fontWeight: "600",
              padding: "10px 20px",
              borderRadius: "6px",
              border: "none",
              cursor: (actionLoading || selectedNodeIds.length === 0) ? "not-allowed" : "pointer",
              opacity: (actionLoading || selectedNodeIds.length === 0) ? 0.5 : 1,
            }}
          >
            {actionLoading ? "Simulating..." : "Run Cascade Simulation"}
          </button>

          {simulationResult && (
            <div style={{ marginTop: "24px", paddingTop: "16px", borderTop: "1px solid #e5e7eb" }}>
              <div style={{ backgroundColor: "#fffbebe6", borderLeft: "4px solid #f59e0b", padding: "16px", borderRadius: "4px", marginBottom: "16px" }}>
                <p style={{ color: "#b45309", fontWeight: "600", margin: 0 }}>
                  Combined Blast Radius: {simulationResult.combined_blast_radius_count} nodes affected
                </p>
              </div>

              <div style={{ overflowX: "auto", border: "1px solid #e5e7eb", borderRadius: "8px" }}>
                <table style={{ width: "100%", borderCollapse: "collapse", textAlignment: "left", fontSize: "14px" }}>
                  <thead style={{ backgroundColor: "#f9fafb" }}>
                    <tr>
                      <th style={{ padding: "10px 16px", textAlign: "left", color: "#4b5563" }}>Affected Node</th>
                      <th style={{ padding: "10px 16px", textAlign: "left", color: "#4b5563" }}>Type</th>
                      <th style={{ padding: "10px 16px", textAlign: "left", color: "#4b5563" }}>Composite Risk Score</th>
                      <th style={{ padding: "10px 16px", textAlign: "left", color: "#4b5563" }}>Cascade Depth</th>
                    </tr>
                  </thead>
                  <tbody>
                    {simulationResult.affected_nodes.map((item) => (
                      <tr key={item.id} style={{ borderTop: "1px solid #e5e7eb" }}>
                        <td style={{ padding: "10px 16px", fontWeight: "500", color: "#111827" }}>{item.name}</td>
                        <td style={{ padding: "10px 16px", color: "#4b5563" }}>{item.type}</td>
                        <td style={{ padding: "10px 16px", color: "#dc2626", fontWeight: "600" }}>{item.composite_risk_score}</td>
                        <td style={{ padding: "10px 16px", color: "#6b7280" }}>Hop {item.depth}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 3: MITIGATION PLANS */}
      {activeTab === "recommendations" && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))", gap: "16px" }}>
          {recommendations.map((plan, idx) => (
            <div
              key={idx}
              style={{
                padding: "20px",
                borderRadius: "8px",
                border: "1px solid #e5e7eb",
                backgroundColor: "#ffffff",
                borderLeft: plan.risk_level === "CRITICAL" ? "5px solid #ef4444" : "5px solid #f59e0b",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "8px" }}>
                <h4 style={{ fontSize: "16px", fontWeight: "bold", color: "#111827", margin: 0 }}>{plan.entity.name}</h4>
                <span
                  style={{
                    fontSize: "12px",
                    fontWeight: "bold",
                    padding: "4px 8px",
                    borderRadius: "12px",
                    backgroundColor: plan.risk_level === "CRITICAL" ? "#fee2e2" : "#fef3c7",
                    color: plan.risk_level === "CRITICAL" ? "#b91c1c" : "#b45309",
                  }}
                >
                  {plan.risk_level}
                </span>
              </div>
              <p style={{ fontSize: "14px", color: "#4b5563", marginBottom: "12px" }}>
                <strong>Composite Risk Score:</strong> {plan.entity.composite_risk_score}
              </p>

              <div style={{ fontSize: "14px" }}>
                <div style={{ marginBottom: "8px" }}>
                  <strong style={{ color: "#1f2937" }}>Identified Vulnerabilities:</strong>
                  <ul style={{ margin: "4px 0 0 0", paddingLeft: "20px", color: "#4b5563" }}>
                    {plan.vulnerabilities.map((v, i) => (
                      <li key={i}>{v}</li>
                    ))}
                  </ul>
                </div>
                <div>
                  <strong style={{ color: "#1f2937" }}>Recommended Actions:</strong>
                  <ul style={{ margin: "4px 0 0 0", paddingLeft: "20px", color: "#374151" }}>
                    {plan.recommended_actions.map((a, i) => (
                      <li key={i}>{a}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default RiskAnalysis;
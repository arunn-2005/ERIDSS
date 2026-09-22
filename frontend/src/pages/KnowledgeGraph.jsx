import React, { useEffect, useState, useMemo, useRef } from "react";
import { useParams, useSearchParams } from "react-router-dom";
import CytoscapeComponent from "react-cytoscapejs";
import { getDocumentGraph } from "../services/documentService";
import GraphSyncButton from "../components/GraphSyncButton"; // <-- 1. Import Component

const TYPE_COLORS = {
  vendor: "#3b82f6",
  customer: "#10b981",
  technology: "#8b5cf6",
  location: "#f59e0b",
  policy: "#ef4444",
  contract: "#6366f1",
  employee: "#ec4899",
  organization: "#14b8a6",
  person: "#ec4899",
  default: "#64748b"
};

export default function KnowledgeGraph() {
  const params = useParams();
  const [searchParams] = useSearchParams();
  const documentId = params.documentId || searchParams.get("documentId");

  const [graphData, setGraphData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedElement, setSelectedElement] = useState(null);
  const cyRef = useRef(null);

  useEffect(() => {
    if (!documentId) {
      setError("No document ID specified in route.");
      setLoading(false);
      return;
    }

    let isMounted = true;

    const loadGraph = async () => {
      try {
        setLoading(true);
        setError(null);

        const response = await getDocumentGraph(documentId);
        const payload =
          response?.nodes && response?.edges
            ? response
            : response?.graph || response?.graph_data || { nodes: [], edges: [] };

        if (isMounted) {
          setGraphData(payload);
        }
      } catch (err) {
        if (isMounted) {
          setError(
            err.response?.data?.detail ||
              err.message ||
              "Failed to load graph data."
          );
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    loadGraph();

    return () => {
      isMounted = false;
    };
  }, [documentId]);

  const elements = useMemo(() => {
    if (!graphData?.nodes || !Array.isArray(graphData.nodes)) return [];

    const nodes = graphData.nodes.map((node) => {
      const id = String(node.id);
      const label = node.label || node.name || id;
      const type = (node.type || "default").toLowerCase();

      return {
        data: {
          id,
          label,
          type,
          color: TYPE_COLORS[type] || TYPE_COLORS.default
        }
      };
    });

    const validIds = new Set(nodes.map((n) => n.data.id));

    const edges = (graphData.edges || [])
      .filter((e) => validIds.has(String(e.source)) && validIds.has(String(e.target)))
      .map((edge) => ({
        data: {
          id: String(edge.id || `${edge.source}-${edge.target}`),
          source: String(edge.source),
          target: String(edge.target),
          label: edge.label || ""
        }
      }));

    return [...nodes, ...edges];
  }, [graphData]);

  const stylesheet = [
    {
      selector: "node",
      style: {
        "background-color": "data(color)",
        label: "data(label)",
        color: "#0f172a",
        "font-size": "11px",
        "font-weight": "bold",
        "text-valign": "bottom",
        "text-margin-y": "6px",
        "text-wrap": "wrap",
        "text-max-width": "110px",
        width: "36px",
        height: "36px",
        "border-width": 2,
        "border-color": "#ffffff"
      }
    },
    {
      selector: "edge",
      style: {
        width: 2,
        "line-color": "#94a3b8",
        "target-arrow-color": "#94a3b8",
        "target-arrow-shape": "triangle",
        "curve-style": "bezier",
        label: "data(label)",
        "font-size": "10px",
        color: "#475569",
        "text-background-color": "#ffffff",
        "text-background-opacity": 0.9,
        "text-background-padding": "2px",
        "text-rotation": "autorotate"
      }
    }
  ];

  const layout = {
    name: "cose",
    idealEdgeLength: 120,
    nodeOverlap: 20,
    refresh: 20,
    fit: true,
    padding: 30,
    componentSpacing: 80,
    nodeRepulsion: 450000
  };

  const handleCyReady = (cy) => {
    cyRef.current = cy;
    cy.on("tap", "node", (evt) => setSelectedElement({ kind: "node", ...evt.target.data() }));
    cy.on("tap", "edge", (evt) => setSelectedElement({ kind: "edge", ...evt.target.data() }));
    cy.on("tap", (evt) => {
      if (evt.target === cy) setSelectedElement(null);
    });
    setTimeout(() => {
      cy.resize();
      cy.fit();
    }, 150);
  };

  if (loading) {
    return <div style={{ padding: "32px", color: "#64748b" }}>Loading Knowledge Graph...</div>;
  }

  if (error) {
    return <div style={{ padding: "24px", color: "#ef4444" }}>{error}</div>;
  }

  return (
    <div style={{ padding: "24px", width: "100%", boxSizing: "border-box" }}>
      <div style={{ marginBottom: "16px" }}>
        <h2 style={{ fontSize: "20px", fontWeight: "700", margin: "0 0 4px 0" }}>
          Knowledge Graph Review
        </h2>
        <span style={{ fontSize: "12px", color: "#64748b", fontFamily: "monospace" }}>
          Document ID: {documentId}
        </span>
      </div>

      <div
        style={{
          display: "flex",
          width: "100%",
          height: "650px",
          border: "1px solid #cbd5e1",
          borderRadius: "8px",
          overflow: "hidden",
          backgroundColor: "#ffffff"
        }}
      >
        <div style={{ flex: 1, height: "100%", position: "relative", backgroundColor: "#f8fafc" }}>
          <CytoscapeComponent
            elements={elements}
            layout={layout}
            stylesheet={stylesheet}
            style={{ width: "100%", height: "100%" }}
            cy={handleCyReady}
            wheelSensitivity={0.2}
          />
        </div>

        <div
          style={{
            width: "300px",
            borderLeft: "1px solid #cbd5e1",
            padding: "16px",
            display: "flex",
            flexDirection: "column",
            justifyContent: "space-between"
          }}
        >
          <div>
            <h3 style={{ margin: "0 0 4px 0", fontSize: "15px", fontWeight: "600" }}>
              Graph Inspector
            </h3>
            <p style={{ margin: "0 0 16px 0", fontSize: "12px", color: "#64748b" }}>
              Click any element to inspect.
            </p>

            {selectedElement ? (
              <div style={{ padding: "12px", backgroundColor: "#f1f5f9", borderRadius: "6px", fontSize: "13px" }}>
                <p style={{ margin: "0 0 4px 0" }}><strong>Type:</strong> {selectedElement.kind}</p>
                <p style={{ margin: "0 0 4px 0" }}><strong>Label:</strong> {selectedElement.label}</p>
                {selectedElement.type && <p style={{ margin: 0 }}><strong>Category:</strong> {selectedElement.type}</p>}
              </div>
            ) : (
              <div style={{ fontSize: "12px", color: "#94a3b8" }}>No element selected.</div>
            )}
          </div>

          {/* 2. Render GraphSyncButton with the current documentId */}
          <div>
            <GraphSyncButton documentId={documentId} />
          </div>
        </div>
      </div>
    </div>
  );
}
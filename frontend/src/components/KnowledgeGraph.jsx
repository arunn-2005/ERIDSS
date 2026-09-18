import React, { useMemo, useState } from "react";
import CytoscapeComponent from "react-cytoscapejs";

const TYPE_COLORS = {
  vendor: "#3b82f6",
  customer: "#10b981",
  technology: "#8b5cf6",
  location: "#f59e0b",
  policy: "#ef4444",
  contract: "#6366f1",
  employee: "#ec4899",
  organization: "#14b8a6",
  default: "#64748b"
};

export default function KnowledgeGraph({ graphData, onApproveForNeo4j }) {
  const [selectedElement, setSelectedElement] = useState(null);

  const elements = useMemo(() => {
    if (!graphData?.nodes) return [];

    const cyNodes = graphData.nodes.map((node) => ({
      data: {
        id: String(node.id),
        label: node.label,
        type: node.type,
        color: TYPE_COLORS[node.type?.toLowerCase()] || TYPE_COLORS.default
      }
    }));

    const cyEdges = (graphData.edges || []).map((edge) => ({
      data: {
        id: String(edge.id),
        source: String(edge.source),
        target: String(edge.target),
        label: edge.label,
        weight: edge.weight
      }
    }));

    return [...cyNodes, ...cyEdges];
  }, [graphData]);

  const stylesheet = [
    {
      selector: "node",
      style: {
        "background-color": "data(color)",
        label: "data(label)",
        color: "#1e293b",
        "font-size": "11px",
        "text-valign": "bottom",
        "text-margin-y": "6px",
        "text-wrap": "wrap",
        "text-max-width": "100px",
        width: "36px",
        height: "36px",
        "border-width": 2,
        "border-color": "#ffffff"
      }
    },
    {
      selector: "node:selected",
      style: {
        "border-width": 4,
        "border-color": "#0284c7"
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
        color: "#334155",
        "text-background-color": "#ffffff",
        "text-background-opacity": 0.9,
        "text-background-padding": "2px",
        "text-rotation": "autorotate"
      }
    },
    {
      selector: "edge:selected",
      style: {
        width: 3,
        "line-color": "#0284c7",
        "target-arrow-color": "#0284c7"
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
    cy.on("tap", "node", (evt) => {
      setSelectedElement({ kind: "node", ...evt.target.data() });
    });
    cy.on("tap", "edge", (evt) => {
      setSelectedElement({ kind: "edge", ...evt.target.data() });
    });
    cy.on("tap", (evt) => {
      if (evt.target === cy) setSelectedElement(null);
    });
  };

  if (!elements.length) {
    return (
      <div className="flex h-96 items-center justify-center border border-dashed border-slate-300 text-slate-500">
        No graph data extracted yet.
      </div>
    );
  }

  return (
    <div className="flex h-[620px] w-full border border-slate-200 rounded-lg overflow-hidden bg-white">
      <div className="flex-1 h-full bg-slate-50">
        <CytoscapeComponent
          elements={elements}
          layout={layout}
          stylesheet={stylesheet}
          style={{ width: "100%", height: "100%" }}
          cy={handleCyReady}
          wheelSensitivity={0.2}
        />
      </div>

      <div className="w-80 border-l border-slate-200 p-4 flex flex-col justify-between bg-white">
        <div>
          <h3 className="font-semibold text-slate-800 text-base mb-1">Graph Inspector</h3>
          <p className="text-xs text-slate-500 mb-4">Click any node or relationship to inspect.</p>

          {selectedElement ? (
            <div className="p-3 bg-slate-50 rounded border border-slate-200 text-sm space-y-2">
              <div>
                <span className="text-xs text-slate-400 uppercase font-semibold">Element</span>
                <p className="font-medium text-slate-700 capitalize">{selectedElement.kind}</p>
              </div>
              <div>
                <span className="text-xs text-slate-400 uppercase font-semibold">Label</span>
                <p className="font-semibold text-slate-900">{selectedElement.label}</p>
              </div>
              {selectedElement.type && (
                <div>
                  <span className="text-xs text-slate-400 uppercase font-semibold">Type</span>
                  <p className="text-slate-700">{selectedElement.type}</p>
                </div>
              )}
            </div>
          ) : (
            <div className="p-3 text-xs text-slate-400 italic bg-slate-50 rounded border border-slate-100">
              Select an element to view details.
            </div>
          )}
        </div>

        <button
          onClick={() => onApproveForNeo4j && onApproveForNeo4j(graphData)}
          className="w-full py-2 px-3 bg-slate-900 hover:bg-slate-800 text-white rounded text-sm font-medium transition"
        >
          Approve for Neo4j Sync
        </button>
      </div>
    </div>
  );
}
import React, { useState } from "react";
import { syncDocumentGraph } from "../services/graphService";

const GraphSyncButton = ({ documentId, onSyncComplete }) => {
  const [loading, setLoading] = useState(false);
  const [statusMsg, setStatusMsg] = useState(null);

  const handleSync = async () => {
    if (!documentId) return;

    setLoading(true);
    setStatusMsg(null);
    try {
      const res = await syncDocumentGraph(documentId);
      setStatusMsg(`Success: Synced ${res.data.nodes_synced} nodes & ${res.data.edges_synced} edges!`);
      if (onSyncComplete) onSyncComplete(res.data);
    } catch (err) {
      console.error("Failed to sync graph:", err);
      setStatusMsg("Error syncing data to Knowledge Graph.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="my-4">
      <button
        onClick={handleSync}
        disabled={loading}
        className="px-4 py-2 bg-indigo-600 text-white font-medium rounded hover:bg-indigo-700 disabled:opacity-50 transition-colors shadow-sm"
      >
        {loading ? "Syncing to Knowledge Graph..." : "Sync to Knowledge Graph"}
      </button>
      {statusMsg && (
        <p className={`text-sm mt-2 font-medium ${statusMsg.startsWith("Success") ? "text-green-600" : "text-red-600"}`}>
          {statusMsg}
        </p>
      )}
    </div>
  );
};

export default GraphSyncButton;
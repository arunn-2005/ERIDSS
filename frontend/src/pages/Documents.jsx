import { useState } from "react";
import DocumentUpload from "../components/Documents/DocumentUpload";
import DocumentTable from "../components/Documents/DocumentTable";
import { runFullDocumentPipeline } from "../services/documentService";
import "../styles/ERIDSSTheme.css";

function Documents() {
  const [refresh, setRefresh] = useState(false);
  const [processingId, setProcessingId] = useState(null);
  const [statusMessage, setStatusMessage] = useState("");

  const handleUploadSuccess = () => {
    setRefresh((prev) => !prev);
  };

  const handleProcess = async (documentId) => {
    try {
      setProcessingId(documentId);
      setStatusMessage("Processing document...");

      // Execute sequential text extraction + entity extraction
      await runFullDocumentPipeline(documentId);

      setStatusMessage("Document processed successfully.");
      setRefresh((prev) => !prev); // Refresh table state
    } catch (error) {
      console.error("Processing failed:", error);
      setStatusMessage(
        error.response?.data?.detail || "Failed to process document."
      );
    } finally {
      setProcessingId(null);
    }
  };

  return (
    <div>
      <div style={{ marginBottom: "30px" }}>
        <h1 style={{ fontSize: "2.2rem", fontWeight: "700", marginBottom: "8px", color: "#ffffff" }}>
          Documents
        </h1>
        <p style={{ color: "#94a3b8", maxWidth: "650px", lineHeight: "1.6" }}>
          Manage and process technical enterprise documentation securely.
        </p>
      </div>

      <div className="eridss-card">
        <DocumentUpload onUploadSuccess={handleUploadSuccess} />
      </div>

      {statusMessage && (
        <div style={{
          background: "#0f172a",
          color: "#93c5fd",
          borderLeft: "4px solid #2563eb",
          padding: "14px 18px",
          borderRadius: "10px",
          marginBottom: "25px",
          fontSize: "14px",
          border: "1px solid #1e293b"
        }}>
          {statusMessage}
        </div>
      )}

      <div className="eridss-card">
        <DocumentTable 
          refresh={refresh} 
          onProcess={handleProcess}
          processingId={processingId}
        />
      </div>
    </div>
  );
}

export default Documents;
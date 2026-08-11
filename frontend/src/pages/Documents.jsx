import { useState } from "react";
import DocumentUpload from "../components/Documents/DocumentUpload";
import DocumentTable from "../components/Documents/DocumentTable";
import { runFullDocumentPipeline } from "../services/documentService";

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
      <h1>Documents</h1>

      <DocumentUpload onUploadSuccess={handleUploadSuccess} />

      {statusMessage && <p className="status-message">{statusMessage}</p>}

      <DocumentTable 
        refresh={refresh} 
        onProcess={handleProcess}
        processingId={processingId}
      />
    </div>
  );
}

export default Documents;
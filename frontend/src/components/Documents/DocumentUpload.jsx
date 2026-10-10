import { useState } from "react";
import { uploadDocument } from "../../services/documentService";

function DocumentUpload({ onUploadSuccess }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
    setMessage("");
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setIsError(true);
      setMessage("Please select a file first.");
      return;
    }

    try {
      setLoading(true);
      setIsError(false);

      await uploadDocument(selectedFile);

      setMessage("Document uploaded successfully.");
      setSelectedFile(null);

      // Clear file input
      document.getElementById("documentInput").value = "";

      // Refresh document table
      if (onUploadSuccess) {
        onUploadSuccess();
      }
    } catch (error) {
      setIsError(true);

      if (error.response?.data?.detail) {
        setMessage(error.response.data.detail);
      } else {
        setMessage("Failed to upload document.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2 style={{ fontSize: "1.4rem", marginBottom: "16px", color: "white" }}>
        Upload Enterprise Document
      </h2>

      <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
        <input
          id="documentInput"
          type="file"
          accept=".pdf,.docx,.txt"
          onChange={handleFileChange}
          style={{
            background: "#0f172a",
            border: "1px dashed #334155",
            padding: "20px",
            borderRadius: "10px",
            color: "#94a3b8",
            cursor: "pointer",
            outline: "none"
          }}
        />

        {selectedFile && (
          <p style={{ color: "#cbd5e1", fontSize: "14px" }}>
            <strong style={{ color: "white" }}>Selected File:</strong> {selectedFile.name}
          </p>
        )}

        {message && (
          <div style={{
            background: isError ? "#3f1111" : "#064e3b",
            color: isError ? "#fecaca" : "#a7f3d0",
            borderLeft: `4px solid ${isError ? "#ef4444" : "#10b981"}`,
            padding: "12px",
            borderRadius: "8px",
            fontSize: "14px"
          }}>
            {message}
          </div>
        )}

        <button
          className="eridss-btn-primary"
          onClick={handleUpload}
          disabled={loading}
          style={{
            width: "fit-content",
            cursor: loading ? "not-allowed" : "pointer",
            opacity: loading ? 0.7 : 1
          }}
        >
          {loading ? "Uploading..." : "Upload Document"}
        </button>
      </div>
    </div>
  );
}

export default DocumentUpload;
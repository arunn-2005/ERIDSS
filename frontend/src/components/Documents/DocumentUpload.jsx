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
    <div
      style={{
        border: "1px solid #d1d5db",
        borderRadius: "10px",
        padding: "25px",
        marginBottom: "30px",
        backgroundColor: "#ffffff",
      }}
    >
      <h2>Upload Enterprise Document</h2>

      <input
        id="documentInput"
        type="file"
        accept=".pdf,.docx,.txt"
        onChange={handleFileChange}
      />

      <br />
      <br />

      {selectedFile && (
        <p>
          <strong>Selected File:</strong> {selectedFile.name}
        </p>
      )}

      {message && (
        <p
          style={{
            color: isError ? "red" : "green",
            fontWeight: "bold",
          }}
        >
          {message}
        </p>
      )}

      <button
        onClick={handleUpload}
        disabled={loading}
        style={{
          padding: "10px 20px",
          cursor: loading ? "not-allowed" : "pointer",
          opacity: loading ? 0.7 : 1,
        }}
      >
        {loading ? "Uploading..." : "Upload Document"}
      </button>
    </div>
  );
}

export default DocumentUpload;
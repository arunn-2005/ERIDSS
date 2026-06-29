import { useState } from "react";

function DocumentUpload() {
  const [selectedFile, setSelectedFile] = useState(null);

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleUpload = () => {
    if (!selectedFile) {
      alert("Please select a file first.");
      return;
    }

    alert(`Selected File: ${selectedFile.name}`);
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
        type="file"
        accept=".pdf,.docx,.txt"
        onChange={handleFileChange}
      />

      <br />
      <br />

      {selectedFile && (
        <p>
          <strong>Selected:</strong> {selectedFile.name}
        </p>
      )}

      <button
        onClick={handleUpload}
        style={{
          padding: "10px 20px",
          cursor: "pointer",
        }}
      >
        Upload Document
      </button>
    </div>
  );
}

export default DocumentUpload;
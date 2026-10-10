import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  getMyDocuments,
  downloadDocument,
  viewDocument,
  deleteDocument,
  processDocument,
  extractEntities,
  extractRelations
} from "../../services/documentService";
import "../../styles/ERIDSSTheme.css";

function DocumentTable({ refresh }) {
  const navigate = useNavigate();

  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [processingId, setProcessingId] = useState(null);

  const [page, setPage] = useState(1);
  const limit = 10;

  // Input values
  const [search, setSearch] = useState("");
  const [fileTypeFilter, setFileTypeFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [sortBy, setSortBy] = useState("file_size");
  const [sortOrder, setSortOrder] = useState("desc");

  // Applied values
  const [appliedSearch, setAppliedSearch] = useState("");
  const [appliedFileType, setAppliedFileType] = useState("");
  const [appliedStatus, setAppliedStatus] = useState("");
  const [appliedSortBy, setAppliedSortBy] = useState("file_size");
  const [appliedSortOrder, setAppliedSortOrder] = useState("desc");

  const loadDocuments = async () => {
    try {
      setLoading(true);

      const data = await getMyDocuments(
        page,
        limit,
        appliedSearch,
        appliedStatus,
        appliedFileType,
        appliedSortBy,
        appliedSortOrder
      );

      setDocuments(data);
    } catch (error) {
      console.error("Error fetching documents:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDocuments();
  }, [
    refresh,
    page,
    appliedSearch,
    appliedStatus,
    appliedFileType,
    appliedSortBy,
    appliedSortOrder,
  ]);

  const applyFilters = () => {
    setPage(1);
    setAppliedSearch(search);
    setAppliedStatus(statusFilter);
    setAppliedFileType(fileTypeFilter);
    setAppliedSortBy(sortBy);
    setAppliedSortOrder(sortOrder);
  };

  const resetFilters = () => {
    setSearch("");
    setFileTypeFilter("");
    setStatusFilter("");
    setSortBy("file_size");
    setSortOrder("desc");

    setAppliedSearch("");
    setAppliedFileType("");
    setAppliedStatus("");
    setAppliedSortBy("file_size");
    setAppliedSortOrder("desc");

    setPage(1);
  };

  const handleProcess = async (documentId) => {
    try {
      setProcessingId(documentId);

      await processDocument(documentId);
      await extractEntities(documentId);
      await extractRelations(documentId);

      alert("Document, entities, and relations processed successfully.");

      loadDocuments();
    } catch (error) {
      console.error("Processing error:", error);

      alert(
        error.response?.data?.detail ||
          "Failed to process document."
      );
    } finally {
      setProcessingId(null);
    }
  };

  const handleDelete = async (documentId) => {
    const confirmDelete = window.confirm(
      "Are you sure you want to delete this document?"
    );

    if (!confirmDelete) return;

    try {
      await deleteDocument(documentId);

      alert("Document deleted successfully.");

      loadDocuments();
    } catch (error) {
      console.error(error);

      alert(
        error.response?.data?.detail ||
          "Failed to delete document."
      );
    }
  };

  return (
    <div>
      <h2 style={{ fontSize: "1.4rem", marginBottom: "20px", color: "white" }}>
        Uploaded Documents
      </h2>

      {/* Search & Filters */}
      <div
        style={{
          display: "flex",
          gap: "12px",
          marginBottom: "22px",
          flexWrap: "wrap",
          alignItems: "center",
        }}
      >
        <input
          type="text"
          className="eridss-input"
          placeholder="Search by filename..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ width: "240px", padding: "10px 14px" }}
        />

        <select
          className="eridss-select"
          value={fileTypeFilter}
          onChange={(e) => setFileTypeFilter(e.target.value)}
          style={{ width: "150px", padding: "10px 14px" }}
        >
          <option value="">All File Types</option>
          <option value=".pdf">PDF</option>
          <option value=".docx">DOCX</option>
          <option value=".txt">TXT</option>
        </select>

        <select
          className="eridss-select"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          style={{ width: "150px", padding: "10px 14px" }}
        >
          <option value="">All Status</option>
          <option value="Uploaded">Uploaded</option>
          <option value="Processed">Processed</option>
          <option value="Failed">Failed</option>
        </select>

        <select
          className="eridss-select"
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          style={{ width: "150px", padding: "10px 14px" }}
        >
          <option value="file_size">File Size</option>
          <option value="filename">Filename</option>
          <option value="uploaded_at">Upload Date</option>
        </select>

        <select
          className="eridss-select"
          value={sortOrder}
          onChange={(e) => setSortOrder(e.target.value)}
          style={{ width: "150px", padding: "10px 14px" }}
        >
          <option value="desc">Descending</option>
          <option value="asc">Ascending</option>
        </select>

        <button className="eridss-btn-primary" onClick={applyFilters} style={{ padding: "10px 18px" }}>
          Search
        </button>

        <button className="eridss-btn-secondary" onClick={resetFilters} style={{ padding: "10px 18px" }}>
          Reset
        </button>
      </div>

      {loading ? (
        <p style={{ color: "#94a3b8", padding: "20px 0" }}>Loading documents...</p>
      ) : (
        <>
          <div style={{ overflowX: "auto" }}>
            <table className="eridss-table">
              <thead>
                <tr>
                  <th>Filename</th>
                  <th>File Type</th>
                  <th>File Size</th>
                  <th>Status</th>
                  <th>Uploaded At</th>
                  <th>Actions</th>
                </tr>
              </thead>

              <tbody>
                {documents.length === 0 ? (
                  <tr>
                    <td colSpan="6" style={{ textAlign: "center", padding: "30px", color: "#64748b" }}>
                      No documents found.
                    </td>
                  </tr>
                ) : (
                  documents.map((doc) => (
                    <tr key={doc.id}>
                      <td style={{ fontWeight: "500", color: "white" }}>{doc.filename}</td>
                      <td>{doc.file_type.toUpperCase()}</td>
                      <td>{(doc.file_size / 1024).toFixed(2)} KB</td>
                      <td>
                        <span style={{
                          padding: "4px 10px",
                          borderRadius: "6px",
                          fontSize: "12px",
                          background: doc.status === "Processed" ? "rgba(16, 185, 129, 0.15)" : "rgba(37, 99, 235, 0.15)",
                          color: doc.status === "Processed" ? "#34d399" : "#60a5fa"
                        }}>
                          {doc.status}
                        </span>
                      </td>
                      <td>{new Date(doc.uploaded_at).toLocaleString()}</td>
                      <td>
                        <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
                          <button
                            title="View"
                            onClick={() => viewDocument(doc.id)}
                            style={{ background: "transparent", border: "none", cursor: "pointer", fontSize: "16px" }}
                          >
                            👁️
                          </button>

                          <button
                            title="Download"
                            onClick={() => downloadDocument(doc.id, doc.filename)}
                            style={{ background: "transparent", border: "none", cursor: "pointer", fontSize: "16px" }}
                          >
                            ⬇️
                          </button>

                          <button
                            title="View Knowledge Graph"
                            onClick={() => navigate(`/knowledge-graph/${doc.id}`)}
                            style={{ background: "transparent", border: "none", cursor: "pointer", fontSize: "16px" }}
                          >
                            🌐
                          </button>

                          <button
                            title="Process Pipeline (Text -> Entities -> Relations)"
                            onClick={() => handleProcess(doc.id)}
                            disabled={
                              processingId === doc.id ||
                              doc.status === "Processing"
                            }
                            style={{
                              background: "transparent",
                              border: "none",
                              cursor:
                                processingId === doc.id ||
                                doc.status === "Processing"
                                  ? "not-allowed"
                                  : "pointer",
                              fontSize: "16px",
                              opacity: processingId === doc.id ? 0.5 : 1
                            }}
                          >
                            {processingId === doc.id ? "⏳" : "⚙️"}
                          </button>

                          <button
                            title="Delete"
                            onClick={() => handleDelete(doc.id)}
                            style={{
                              background: "transparent",
                              border: "none",
                              cursor: "pointer",
                              fontSize: "16px",
                            }}
                          >
                            🗑️
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div
            style={{
              marginTop: "25px",
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              gap: "20px",
            }}
          >
            <button
              className="eridss-btn-secondary"
              disabled={page === 1}
              onClick={() => setPage(page - 1)}
              style={{ padding: "8px 16px", opacity: page === 1 ? 0.5 : 1 }}
            >
              Previous
            </button>

            <strong style={{ color: "#cbd5e1" }}>Page {page}</strong>

            <button
              className="eridss-btn-secondary"
              disabled={documents.length < limit}
              onClick={() => setPage(page + 1)}
              style={{ padding: "8px 16px", opacity: documents.length < limit ? 0.5 : 1 }}
            >
              Next
            </button>
          </div>
        </>
      )}
    </div>
  );
}

export default DocumentTable;
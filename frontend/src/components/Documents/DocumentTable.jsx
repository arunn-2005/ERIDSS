import { useEffect, useState } from "react";
import {
  getMyDocuments,
  downloadDocument,
  viewDocument,
  deleteDocument,
  processDocument,
} from "../../services/documentService";
function DocumentTable({ refresh }) {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);

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
    await processDocument(documentId);

    alert("Document processed successfully.");

    loadDocuments(); // Refresh the table
  } catch (error) {
    console.error(error);

    alert(
      error.response?.data?.detail ||
      "Failed to process document."
    );
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
    <div style={{ marginTop: "30px" }}>
      <h2>Uploaded Documents</h2>

      {/* Search & Filters */}

      <div
        style={{
          display: "flex",
          gap: "15px",
          marginBottom: "20px",
          flexWrap: "wrap",
          alignItems: "center",
        }}
      >
        <input
          type="text"
          placeholder="Search by filename..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{
            padding: "8px",
            width: "250px",
          }}
        />

        <select
          value={fileTypeFilter}
          onChange={(e) => setFileTypeFilter(e.target.value)}
        >
          <option value="">All File Types</option>
          <option value=".pdf">PDF</option>
          <option value=".docx">DOCX</option>
          <option value=".txt">TXT</option>
        </select>

        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
        >
          <option value="">All Status</option>
          <option value="Uploaded">Uploaded</option>
          <option value="Processed">Processed</option>
          <option value="Failed">Failed</option>
        </select>

        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
        >
          <option value="file_size">File Size</option>
          <option value="filename">Filename</option>
          <option value="uploaded_at">Upload Date</option>
        </select>

        <select
          value={sortOrder}
          onChange={(e) => setSortOrder(e.target.value)}
        >
          <option value="desc">Descending</option>
          <option value="asc">Ascending</option>
        </select>

        <button onClick={applyFilters}>
          Search
        </button>

        <button onClick={resetFilters}>
          Reset
        </button>
      </div>

      {loading ? (
        <p>Loading documents...</p>
      ) : (
        <>
          <table
            border="1"
            cellPadding="10"
            style={{
              width: "100%",
              borderCollapse: "collapse",
            }}
          >
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
                  <td colSpan="5" style={{ textAlign: "center" }}>
                    No documents found.
                  </td>
                </tr>
              ) : (
                documents.map((doc) => (
                  <tr key={doc.id}>
                    <td>{doc.filename}</td>
                    <td>{doc.file_type.toUpperCase()}</td>
                    <td>{(doc.file_size / 1024).toFixed(2)} KB</td>
                    <td>{doc.status}</td>
                    <td>{new Date(doc.uploaded_at).toLocaleString()}</td>
                     <td>
  <button
    title="View"
    onClick={() => viewDocument(doc.id)}
    style={{
      marginRight: "8px",
      cursor: "pointer",
    }}
  >
    👁️
  </button>

  <button
    title="Download"
    onClick={() => downloadDocument(doc.id, doc.filename)}
    style={{
      marginRight: "8px",
      cursor: "pointer",
    }}
  >
    ⬇️
  </button>

  <button
    title="Process"
    onClick={() => handleProcess(doc.id)}
    disabled={
      doc.status === "Processing" ||
      doc.status === "Processed"
    }
    style={{
      marginRight: "8px",
      cursor:
        doc.status === "Processing" ||
        doc.status === "Processed"
          ? "not-allowed"
          : "pointer",
    }}
  >
    ⚙️
  </button>

  <button
    title="Delete"
    onClick={() => handleDelete(doc.id)}
    style={{
      cursor: "pointer",
      color: "red",
    }}
  >
    🗑️
  </button>
</td>

                  </tr>
                ))
              )}
            </tbody>
          </table>

          {/* Pagination */}

          <div
            style={{
              marginTop: "20px",
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              gap: "20px",
            }}
          >
            <button
              disabled={page === 1}
              onClick={() => setPage(page - 1)}
            >
              Previous
            </button>

            <strong>Page {page}</strong>

            <button
              disabled={documents.length < limit}
              onClick={() => setPage(page + 1)}
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
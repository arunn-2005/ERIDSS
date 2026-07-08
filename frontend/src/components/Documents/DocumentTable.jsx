import { useEffect, useState } from "react";
import { getMyDocuments } from "../../services/documentService";

function DocumentTable({ refresh }) {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);

  const [page, setPage] = useState(1);
  const limit = 10;

  // Input values
  const [search, setSearch] = useState("");
  const [fileTypeFilter, setFileTypeFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");

  // Applied values (used for API calls)
  const [appliedSearch, setAppliedSearch] = useState("");
  const [appliedFileType, setAppliedFileType] = useState("");
  const [appliedStatus, setAppliedStatus] = useState("");

  const loadDocuments = async () => {
    try {
      setLoading(true);

      const data = await getMyDocuments(
        page,
        limit,
        appliedSearch,
        appliedStatus,
        appliedFileType
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
  }, [refresh, page, appliedSearch, appliedStatus, appliedFileType]);

  const applyFilters = () => {
    setPage(1);
    setAppliedSearch(search);
    setAppliedStatus(statusFilter);
    setAppliedFileType(fileTypeFilter);
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
          <option value="pdf">PDF</option>
          <option value="docx">DOCX</option>
          <option value="txt">TXT</option>
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

        <button onClick={applyFilters}>
          Search
        </button>

        <button
          onClick={() => {
            setSearch("");
            setStatusFilter("");
            setFileTypeFilter("");

            setAppliedSearch("");
            setAppliedStatus("");
            setAppliedFileType("");

            setPage(1);
          }}
        >
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
                  </tr>
                ))
              )}
            </tbody>
          </table>

          <div
            style={{
              marginTop: "20px",
              display: "flex",
              justifyContent: "center",
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
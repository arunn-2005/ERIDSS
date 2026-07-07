import { useEffect, useState } from "react";
import { getMyDocuments } from "../../services/documentService";

function DocumentTable({ refresh }) {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);

  const [page, setPage] = useState(1);
  const limit = 10;

  const loadDocuments = async () => {
    try {
      setLoading(true);

      const data = await getMyDocuments(page, limit);

      setDocuments(data);
    } catch (error) {
      console.error("Error fetching documents:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDocuments();
  }, [refresh, page]);

  if (loading) {
    return <p>Loading documents...</p>;
  }

  return (
    <div style={{ marginTop: "30px" }}>
      <h2>Uploaded Documents</h2>

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
                No documents uploaded yet.
              </td>
            </tr>
          ) : (
            documents.map((doc) => (
              <tr key={doc.id}>
                <td>{doc.filename}</td>
                <td>{doc.file_type}</td>
                <td>{(doc.file_size / 1024).toFixed(2)} KB</td>
                <td>{doc.status}</td>
                <td>{new Date(doc.uploaded_at).toLocaleString()}</td>
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
          gap: "15px",
        }}
      >
        <button
          onClick={() => setPage(page - 1)}
          disabled={page === 1}
        >
          Previous
        </button>

        <span>
          Page {page}
        </span>

        <button
          onClick={() => {
            if (documents.length === limit) {
              setPage(page + 1);
            }
          }}
          disabled={documents.length < limit}
        >
          Next
        </button>
      </div>
    </div>
  );
}

export default DocumentTable;
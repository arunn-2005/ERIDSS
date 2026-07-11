import { useEffect, useState } from "react";
import {
  getAllDocuments,
  downloadDocument,
} from "../services/adminService";

function AdminDocuments() {
  const [documents, setDocuments] = useState([]);

  const [page, setPage] = useState(1);
  const limit = 10;

  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");
  const [fileType, setFileType] = useState("");

  const [sort, setSort] = useState("uploaded_at");
  const [order, setOrder] = useState("desc");

  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDocuments();
  }, [page, status, fileType, sort, order]);

  const fetchDocuments = async () => {
    try {
      setLoading(true);

      const data = await getAllDocuments(
        page,
        limit,
        search,
        status,
        fileType,
        sort,
        order
      );

      console.log(data);

      setDocuments(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    setPage(1);
    fetchDocuments();
  };

  const handleReset = () => {
    setSearch("");
    setStatus("");
    setFileType("");
    setSort("uploaded_at");
    setOrder("desc");
    setPage(1);
  };

  // ===============================
  // Download Document
  // ===============================
  const handleDownload = async (documentId, filename) => {
    try {
      const response = await downloadDocument(documentId);

      const url = window.URL.createObjectURL(
        new Blob([response.data])
      );

      const link = document.createElement("a");

      link.href = url;
      link.setAttribute("download", filename);

      document.body.appendChild(link);

      link.click();

      link.remove();

      window.URL.revokeObjectURL(url);

    } catch (error) {
      console.error(error);
      alert("Failed to download document.");
    }
  };

  return (
    <div style={{ padding: "30px" }}>
      <h1>All Uploaded Documents</h1>

      <br />

      <div
        style={{
          display: "flex",
          gap: "10px",
          flexWrap: "wrap",
          marginBottom: "20px",
        }}
      >
        <input
          type="text"
          placeholder="Search filename..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />

        <select
          value={fileType}
          onChange={(e) => setFileType(e.target.value)}
        >
          <option value="">All Types</option>
          <option value=".pdf">PDF</option>
          <option value=".docx">DOCX</option>
          <option value=".txt">TXT</option>
        </select>

        <select
          value={status}
          onChange={(e) => setStatus(e.target.value)}
        >
          <option value="">All Status</option>
          <option value="Uploaded">Uploaded</option>
          <option value="Processing">Processing</option>
          <option value="Processed">Processed</option>
          <option value="Failed">Failed</option>
        </select>

        <select
          value={sort}
          onChange={(e) => setSort(e.target.value)}
        >
          <option value="uploaded_at">Upload Date</option>
          <option value="filename">Filename</option>
          <option value="status">Status</option>
          <option value="username">Username</option>
        </select>

        <select
          value={order}
          onChange={(e) => setOrder(e.target.value)}
        >
          <option value="desc">Descending</option>
          <option value="asc">Ascending</option>
        </select>

        <button onClick={handleSearch}>Search</button>

        <button onClick={handleReset}>Reset</button>
      </div>

      {loading ? (
        <h3>Loading...</h3>
      ) : (
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
              <th>Status</th>
              <th>Username</th>
              <th>Email</th>
              <th>Uploaded At</th>
              <th>Actions</th>
            </tr>
          </thead>

          <tbody>
            {documents.length === 0 ? (
              <tr>
                <td colSpan="7" align="center">
                  No documents found.
                </td>
              </tr>
            ) : (
              documents.map((doc) => (
                <tr key={doc.id}>
                  <td>{doc.filename}</td>
                  <td>{doc.file_type}</td>
                  <td>{doc.status}</td>
                  <td>{doc.username}</td>
                  <td>{doc.email}</td>
                  <td>
                    {new Date(doc.uploaded_at).toLocaleString()}
                  </td>

                  <td>
                    <button
                      onClick={() =>
                        handleDownload(doc.id, doc.filename)
                      }
                    >
                      Download
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      )}

      <br />

      <div
        style={{
          display: "flex",
          justifyContent: "center",
          gap: "15px",
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
    </div>
  );
}

export default AdminDocuments;
function DocumentTable() {
  return (
    <div>
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
            <th>Status</th>
            <th>Upload Date</th>
            <th>Actions</th>
          </tr>
        </thead>

        <tbody>
          <tr>
            <td colSpan="4" style={{ textAlign: "center" }}>
              No documents uploaded yet.
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  );
}

export default DocumentTable;
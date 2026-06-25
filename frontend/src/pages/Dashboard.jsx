function Dashboard() {
  return (
    <div>
      <h1>ERIDSS Dashboard</h1>

      <div
        style={{
          display: "flex",
          gap: "20px",
          marginTop: "30px",
        }}
      >
        <div
          style={{
            border: "1px solid #ccc",
            padding: "20px",
            borderRadius: "10px",
            width: "200px",
          }}
        >
          <h3>Documents</h3>
          <p>0 Uploaded</p>
        </div>

        <div
          style={{
            border: "1px solid #ccc",
            padding: "20px",
            borderRadius: "10px",
            width: "200px",
          }}
        >
          <h3>Entities</h3>
          <p>0 Extracted</p>
        </div>

        <div
          style={{
            border: "1px solid #ccc",
            padding: "20px",
            borderRadius: "10px",
            width: "200px",
          }}
        >
          <h3>Risks</h3>
          <p>0 Detected</p>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
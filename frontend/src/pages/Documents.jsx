import { useState } from "react";
import DocumentUpload from "../components/Documents/DocumentUpload";
import DocumentTable from "../components/Documents/DocumentTable";

function Documents() {
  const [refresh, setRefresh] = useState(false);

  const handleUploadSuccess = () => {
    setRefresh((prev) => !prev);
  };

  return (
    <div>
      <h1>Documents</h1>

      <DocumentUpload onUploadSuccess={handleUploadSuccess} />

      <DocumentTable refresh={refresh} />
    </div>
  );
}

export default Documents;
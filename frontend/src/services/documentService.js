import axios from "axios";

const API = "http://127.0.0.1:8000/documents";

const getToken = () => localStorage.getItem("access_token") || localStorage.getItem("token");

const getAuthHeaders = (isMultipart = false) => {
  const token = getToken();
  return {
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(isMultipart ? { "Content-Type": "multipart/form-data" } : {}),
    },
  };
};

// -----------------------------
// Upload Document
// -----------------------------
export const uploadDocument = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await axios.post(`${API}/upload`, formData, getAuthHeaders(true));
  return response.data;
};

// -----------------------------
// Get My Documents
// -----------------------------
export const getMyDocuments = async (
  page = 1,
  limit = 10,
  search = "",
  status = "",
  file_type = "",
  sort = "file_size",
  order = "desc"
) => {
  const response = await axios.get(`${API}/my-documents`, {
    ...getAuthHeaders(),
    params: { page, limit, search, status, file_type, sort, order },
  });
  return response.data;
};

// -----------------------------
// Download Document
// -----------------------------
export const downloadDocument = async (documentId, filename) => {
  const response = await axios.get(`${API}/${documentId}/download`, {
    ...getAuthHeaders(),
    responseType: "blob",
  });

  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", filename);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
};

// -----------------------------
// View Document
// -----------------------------
export const viewDocument = async (documentId) => {
  const response = await axios.get(`${API}/${documentId}/view`, {
    ...getAuthHeaders(),
    responseType: "blob",
  });

  const blobUrl = window.URL.createObjectURL(response.data);
  window.open(blobUrl, "_blank");
};

// -----------------------------
// Delete Document
// -----------------------------
export const deleteDocument = async (documentId) => {
  const response = await axios.delete(`${API}/${documentId}`, getAuthHeaders());
  return response.data;
};

// -----------------------------
// 1. Text Extraction
// -----------------------------
export const processDocument = async (documentId) => {
  const response = await axios.post(`${API}/${documentId}/process`, {}, getAuthHeaders());
  return response.data;
};

// -----------------------------
// 2. Entity Extraction
// -----------------------------
export const extractEntities = async (documentId) => {
  const response = await axios.post(`${API}/${documentId}/extract-entities`, {}, getAuthHeaders());
  return response.data;
};

// -----------------------------
// 3. Relation Extraction
// -----------------------------
export const extractRelations = async (documentId) => {
  const response = await axios.post(`${API}/${documentId}/extract-relations`, {}, getAuthHeaders());
  return response.data;
};

// -----------------------------
// 4. Document Graph
// -----------------------------
export const getDocumentGraph = async (documentId) => {
  const token = getToken();
  if (!token) {
    throw new Error("No authentication token found. Please log in again.");
  }

  const response = await axios.get(`${API}/${documentId}/graph`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return response.data;
};

// -----------------------------
// Full Processing Pipeline
// -----------------------------
export const runFullDocumentPipeline = async (documentId) => {
  await processDocument(documentId);
  await extractEntities(documentId);
  await extractRelations(documentId);
  return { message: "Document, entities, and relationships processed successfully." };
};
import axios from "axios";

const API = "http://127.0.0.1:8000/documents";

const getToken = () => localStorage.getItem("access_token");

// -----------------------------
// Upload Document
// -----------------------------
export const uploadDocument = async (file) => {
    const formData = new FormData();
    formData.append("file", file);

    const response = await axios.post(
        `${API}/upload`,
        formData,
        {
            headers: {
                Authorization: `Bearer ${getToken()}`,
                "Content-Type": "multipart/form-data",
            },
        }
    );

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

    const response = await axios.get(
        `${API}/my-documents`,
        {
            headers: {
                Authorization: `Bearer ${getToken()}`
            },

            params: {
                page,
                limit,
                search,
                status,
                file_type,
                sort,
                order
            }
        }
    );

    return response.data;
};
// -----------------------------
// Download Document
// -----------------------------
export const downloadDocument = async (documentId, filename) => {
    const response = await axios.get(
        `${API}/${documentId}/download`,
        {
            headers: {
                Authorization: `Bearer ${getToken()}`
            },
            responseType: "blob"
        }
    );

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
  const token = getToken();

  const url = `${API}/${documentId}/view`;

  const response = await axios.get(url, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
    responseType: "blob",
  });

  const blobUrl = window.URL.createObjectURL(response.data);

  window.open(blobUrl, "_blank");
};
// -----------------------------
// Delete Document
// -----------------------------
export const deleteDocument = async (documentId) => {
  const response = await axios.delete(
    `${API}/${documentId}`,
    {
      headers: {
        Authorization: `Bearer ${getToken()}`
      }
    }
  );

  return response.data;
};
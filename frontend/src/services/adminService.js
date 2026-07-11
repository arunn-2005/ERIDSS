import api from "./api";

// Dashboard Statistics
export const getDashboard = async () => {
  const response = await api.get("/admin/dashboard");
  return response.data;
};

// All Users
export const getUsers = async () => {
  const response = await api.get("/admin/users");
  return response.data;
};

// Get Single User
export const getUser = async (id) => {
  const response = await api.get(`/admin/users/${id}`);
  return response.data;
};

// Update User Role
export const updateRole = async (id, role) => {
  const response = await api.put(
    `/admin/users/${id}/role`,
    { role }
  );

  return response.data;
};

// Delete User
export const deleteUser = async (id) => {
  const response = await api.delete(`/admin/users/${id}`);
  return response.data;
};
export const getAllDocuments = async (
  page = 1,
  limit = 10,
  search = "",
  status = "",
  file_type = "",
  sort = "uploaded_at",
  order = "desc"
) => {

  const response = await api.get(
    "/admin/documents/get_all_documents",
    {
      params: {
        page,
        limit,
        search,
        status,
        file_type,
        sort,
        order,
      },
    }
  );

  return response.data;
};
// ================================
// Document Dashboard
// ================================


// ==============================
// Document Dashboard
// ==============================

export const getDocumentDashboard = async () => {
  const response = await api.get("/admin/documents/dashboard");
  return response.data;
};

// ===============================
// Download Document
// ===============================

export const downloadDocument = async (documentId) => {
  const response = await api.get(
    `/admin/documents/${documentId}/download`,
    {
      responseType: "blob",
    }
  );

  return response;
};
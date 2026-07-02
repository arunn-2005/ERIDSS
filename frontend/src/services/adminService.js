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
import api from "./api";

export const registerUser = async (userData) => {
  const response = await api.post("/users/register", userData);
  return response.data;
};

export const loginUser = async (credentials) => {
  const response = await api.post("/auth/login", credentials);
  return response.data;
};

export const getProfile = async () => {
  const response = await api.get("/users/me");
  return response.data;
};
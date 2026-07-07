import axios from "axios";

const API = "http://127.0.0.1:8000/documents";

const getToken = () => localStorage.getItem("access_token");

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

export const getMyDocuments = async (
    page = 1,
    limit = 10,
    search = "",
    status = "",
    file_type = ""
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
                file_type
            }
        }
    );

    return response.data;
};
import axios from 'axios';

const API_URL = 'http://localhost:8000';

export const analyzeContent = async (formData) => {
    try {
        // Axios automatically sets Content-Type to multipart/form-data when data is FormData
        const response = await axios.post(`${API_URL}/analyze`, formData);
        return response.data;
    } catch (error) {
        console.error("API call failed:", error);
        throw error;
    }
};

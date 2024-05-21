// export const generateImage = async (text) => {
//   const response = await fetch('/api/images/generate', {
//     method: 'POST',
//     headers: {
//       'Content-Type': 'application/json',
//     },
//     body: JSON.stringify({ text, options: {} }),
//   });
//   const blob = await response.blob();
//   return URL.createObjectURL(blob);
// };

import axios from 'axios';

const API_BASE_URL = 'http://localhost:5002';

export const generateImage = async (data) => {
    try {
        console.log('checkkkkk', data);
        const response = await axios.post(`${API_BASE_URL}/api/images/generate`, {"data": data});
        console.log(response.data);
        return response.data;
    } catch (error) {
        console.error('Error generating image:', error);
        throw error;
    }
};

export const getTaskStatus = async (taskId) => {
    try {
        const response = await axios.get(`${API_BASE_URL}/api/images/status/${taskId}/`);
        return response.data;
    } catch (error) {
        console.error('Error fetching task status:', error);
        throw error;
    }
};
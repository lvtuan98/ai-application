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

const API_BE_URL = process.env.REACT_APP_BE_URL;

export const generateImage = async (data) => {
    try {
        const response = await axios.post(`${API_BE_URL}/generate`, {"data": data});
        return response.data;
    } catch (error) {
        console.error('Error generating image:', error);
        throw error;
    }
};

// export const getTaskStatus = async (taskId) => {
//     try {
//         console.log("api:", `${API_BE_URL}/status/${taskId}`);
//         const response = await axios.get(`${API_BE_URL}/status/${taskId}`);
//         console.log("getTaskStatus", response);
//         // return response.data;
//         if (response.data.state === 'SUCCESS') {
//             return response.data;
//         } else {
//         // If task is still pending, poll again after 2 seconds
//             setTimeout(() => getTaskStatus(taskId), 2000);
//         }

//     } catch (error) {
//         console.error('Error fetching task status:', error);
//         throw error;
//     }
// };


export const getTaskStatus = async (taskId) => {
const checkStatus = async (resolve, reject) => {
    try {
    const response = await axios.get(`${API_BE_URL}/status/${taskId}`);
    if (response.data.state === 'SUCCESS') {
        resolve(response.data.result);
    } else if (response.data.state === 'FAILURE') {
        reject('Image generation failed.');
    } else {
        setTimeout(() => checkStatus(resolve, reject), 2000);
    }
    } catch (error) {
    reject('Error checking task status.');
    }
};

return new Promise(checkStatus);
};
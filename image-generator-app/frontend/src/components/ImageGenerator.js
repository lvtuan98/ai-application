// import React, { useState } from 'react';
// import ImagePreview from './ImagePreview';
// import { generateImage } from '../services/apiService';
// import { getTaskStatus } from '../services/apiService';

// function ImageGenerator() {
//   // const [taskId, setTaskId] = useState(null);
//   const [text, setText] = useState('');
//   const [image, setImage] = useState(null);
//   const [loading, setLoading] = useState(false);


//   const handleGenerate = async () => {
//     setLoading(true);
//     setImage(null)

//     const response = await generateImage(text);
//     console.log("imageData", response);
//     const taskId = response.task_id;
//     console.log("taskId", taskId);
//     // setTaskId(response.task_id);

//     const status = await getTaskStatus(taskId);
//     console.log("status", status)
//     setImage(status.result)
//   };

//   // const handleCheckStatus = async () => {
//   //     if (taskId) {
//   //         const response = await getTaskStatus(taskId);
//   //         console.log("handleCheckStatus", response)
//   //         setImage(response.result);
//   //     }
//   // };


//   return (
//     <div>
//       <input
//         type="text"
//         value={text}
//         onChange={(e) => setText(e.target.value)}
//         placeholder="Enter text"
//       />
//       <button onClick={handleGenerate}>Generate Image</button>
//       {image && <ImagePreview image={image} />}
//     </div>
//   );
// }
// export default ImageGenerator;


import React, { useState } from 'react';
import ImagePreview from './ImagePreview';
import { generateImage, getTaskStatus } from '../services/apiService';

function ImageGenerator() {
  const [text, setText] = useState('');
  const [image, setImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleGenerate = async () => {
    setLoading(true);
    setImage(null);
    setError('');

    try {
      const response = await generateImage(text);
      const taskId = response.task_id;

      const result = await getTaskStatus(taskId);
      setImage(result);
    } catch (error) {
      setError(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input
        type="text"
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Enter text"
      />
      <button onClick={handleGenerate} disabled={loading}>
        {loading ? 'Generating...' : 'Generate Image'}
      </button>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {image && <ImagePreview image={image} />}
    </div>
  );
}

export default ImageGenerator;
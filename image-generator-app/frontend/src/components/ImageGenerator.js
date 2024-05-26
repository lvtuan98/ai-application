import React, { useState } from 'react';
import ImagePreview from './ImagePreview';
import { generateImage } from '../services/apiService';
import { getTaskStatus } from '../services/apiService';

function ImageGenerator() {
  const [text, setText] = useState('');
  const [image, setImage] = useState(null);

  const handleGenerate = async () => {
    const response = await generateImage(text);
    console.log("imageData", response);
    const taskId = response.task_id;
    console.log("taskId", taskId);

    const statusResponse = await getTaskStatus(taskId);
    console.log("statusResponse", statusResponse);

    setImage(statusResponse.result);
  };


  return (
    <div>
      <input
        type="text"
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Enter text"
      />
      <button onClick={handleGenerate}>Generate Image</button>
      {image && <ImagePreview image={image} />}
    </div>
  );
}
export default ImageGenerator;
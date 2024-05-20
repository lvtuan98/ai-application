import React, { useState } from 'react';
import ImagePreview from './ImagePreview';
import { generateImage } from '../services/apiService';

function ImageGenerator() {
  const [text, setText] = useState('');
  const [image, setImage] = useState(null);

  const handleGenerate = async () => {
    const imageData = await generateImage(text);
    setImage(imageData);
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

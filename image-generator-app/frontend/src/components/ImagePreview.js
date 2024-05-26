import React from 'react';

function ImagePreview({ image }) {
  return (
    <div>
      <h2>Generated Image</h2>
      {/* <img src={`data:image/png;base64, ${image}`} alt="Generated" /> */}
      <img src={image} alt="Generated" />
    </div>
  );
}

export default ImagePreview;

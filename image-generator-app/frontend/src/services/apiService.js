export const generateImage = async (text) => {
  const response = await fetch('/api/images/generate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ text, options: {} }),
  });
  const blob = await response.blob();
  return URL.createObjectURL(blob);
};

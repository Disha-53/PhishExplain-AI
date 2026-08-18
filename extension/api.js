async function analyzeRequest(payload) {
  const response = await fetch('http://127.0.0.1:8000/analyze', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    throw new Error('Backend request failed');
  }

  return response.json();
}

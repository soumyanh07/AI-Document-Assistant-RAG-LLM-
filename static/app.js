const uploadForm = document.getElementById('uploadForm');
const chatForm = document.getElementById('chatForm');
const uploadStatus = document.getElementById('uploadStatus');
const messages = document.getElementById('messages');

uploadForm?.addEventListener('submit', async (event) => {
  event.preventDefault();
  const formData = new FormData(uploadForm);
  uploadStatus.textContent = 'Uploading documents...';

  const response = await fetch('/api/documents/upload', {
    method: 'POST',
    body: formData,
  });

  const payload = await response.json();
  uploadStatus.textContent = `Uploaded ${payload.documents?.length || 0} file(s). Total chunks: ${payload.total_chunks || 0}`;
});

chatForm?.addEventListener('submit', async (event) => {
  event.preventDefault();
  const question = document.getElementById('question').value.trim();
  if (!question) {
    messages.innerHTML = '<div class="message">Please enter a question first.</div>';
    return;
  }

  messages.innerHTML = '<div class="message">Thinking...</div>';

  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  });

  const payload = await response.json();
  if (!response.ok) {
    messages.innerHTML = `<div class="message">${payload.detail || 'Unable to process your request.'}</div>`;
    return;
  }

  messages.innerHTML = `
    <div class="message"><strong>Answer</strong><br>${payload.answer}</div>
    <div class="message"><strong>Sources</strong><br>${payload.sources.map((source) => `• ${source.text}`).join('<br>')}</div>
  `;
});

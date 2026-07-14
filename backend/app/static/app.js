const uploadForm = document.getElementById('uploadForm');
const chatForm = document.getElementById('chatForm');
const uploadStatus = document.getElementById('uploadStatus');
const messages = document.getElementById('messages');

const renderMessage = (text, role = 'assistant') => {
  const wrapper = document.createElement('div');
  wrapper.className = `message ${role}`;
  wrapper.innerHTML = text;
  return wrapper;
};

uploadForm?.addEventListener('submit', async (event) => {
  event.preventDefault();
  const formData = new FormData(uploadForm);
  uploadStatus.textContent = 'Uploading documents...';

  try {
    const response = await fetch('/api/documents/upload', {
      method: 'POST',
      body: formData,
    });
    const payload = await response.json();
    const fileNames = payload.documents
      ?.map((doc) => `${doc.name} (${doc.chunks || 0} chunks)`)
      .join(', ') || 'No files';
    uploadStatus.textContent = `Uploaded: ${fileNames}. Total chunks: ${payload.total_chunks || 0}`;
  } catch (error) {
    uploadStatus.textContent = 'Upload failed. Try again.';
  }
});

chatForm?.addEventListener('submit', async (event) => {
  event.preventDefault();
  const questionInput = document.getElementById('question');
  const question = questionInput?.value.trim();
  if (!question) {
    messages.innerHTML = '';
    messages.appendChild(renderMessage('Please enter a question first.', 'user'));
    return;
  }

  messages.innerHTML = '';
  messages.appendChild(renderMessage(`<strong>Question</strong><br>${question}`, 'user'));
  messages.appendChild(renderMessage('Looking through your documents...', 'assistant'));

  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question }),
    });

    const payload = await response.json();
    messages.innerHTML = '';
    if (!response.ok) {
      messages.appendChild(renderMessage(payload.detail || 'Unable to process your request.', 'assistant'));
      return;
    }

    messages.appendChild(renderMessage(`<strong>Answer</strong><br>${payload.answer}`, 'assistant'));

    if (payload.sources && payload.sources.length) {
      const sourceHtml = payload.sources
        .map((source) => `• <strong>${source.source}</strong>: ${source.text}`)
        .join('<br>');
      messages.appendChild(renderMessage(`<strong>Sources</strong><br>${sourceHtml}`, 'assistant'));
    }
  } catch (error) {
    messages.innerHTML = '';
    messages.appendChild(renderMessage('Unable to reach the assistant. Please try again later.', 'assistant'));
  }
});

import { useState } from 'react';

export default function ChatPanel() {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [sources, setSources] = useState([]);

  async function handleSubmit(event) {
    event.preventDefault();
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question }),
    });
    const payload = await response.json();
    setAnswer(payload.answer || '');
    setSources(payload.sources || []);
  }

  return (
    <form onSubmit={handleSubmit}>
      <input value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="Ask a question" />
      <button type="submit">Ask</button>
      <div>{answer}</div>
      <ul>{sources.map((source, index) => <li key={index}>{source.text}</li>)}</ul>
    </form>
  );
}

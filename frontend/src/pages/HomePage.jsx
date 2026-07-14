import ChatPanel from '../components/ChatPanel';

export default function HomePage() {
  return (
    <main>
      <h1>AI Document Assistant</h1>
      <p>Upload documents and ask questions from your own knowledge base.</p>
      <ChatPanel />
    </main>
  );
}

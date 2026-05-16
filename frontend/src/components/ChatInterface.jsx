import { useState, useRef, useEffect } from "react";

export default function ChatInterface() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = { role: "user", content: input };
    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setInput("");
    setIsLoading(true);

    try {
      const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";
      const response = await fetch(`${apiUrl}/api/v1/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: newMessages }),
      });

      if (!response.ok) {
        throw new Error("Failed to fetch response");
      }

      const data = await response.json();
      setMessages((prev) => [...prev, { role: "assistant", content: data.response }]);
    } catch (error) {
      console.error(error);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Sorry, I encountered an error. Please try again." },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="card chat-container" style={{ display: 'flex', flexDirection: 'column', height: '100%', marginTop: '20px' }}>
      <h2 style={{ marginBottom: '15px' }}>F1 AI Analyst Chat</h2>
      <div className="chat-messages" style={{ flexGrow: 1, overflowY: 'auto', padding: '10px', backgroundColor: 'rgba(0,0,0,0.2)', borderRadius: '8px', marginBottom: '15px' }}>
        {messages.length === 0 ? (
          <p style={{ color: 'var(--text-secondary)', textAlign: 'center', marginTop: '20px' }}>
            Ask me anything about F1 strategy, past races, or driver stats!
          </p>
        ) : (
          messages.map((msg, index) => (
            <div key={index} style={{
              marginBottom: '10px',
              padding: '10px',
              borderRadius: '8px',
              backgroundColor: msg.role === 'user' ? 'rgba(225, 6, 0, 0.2)' : 'rgba(255, 255, 255, 0.1)',
              alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
              marginLeft: msg.role === 'user' ? '20%' : '0',
              marginRight: msg.role === 'user' ? '0' : '20%',
              border: msg.role === 'user' ? '1px solid var(--f1-red)' : '1px solid #444',
            }}>
              <strong style={{ color: msg.role === 'user' ? 'var(--f1-red)' : '#fff', display: 'block', marginBottom: '5px' }}>
                {msg.role === 'user' ? 'You' : 'Analyst'}
              </strong>
              <div style={{ whiteSpace: 'pre-wrap', lineHeight: '1.4' }}>{msg.content}</div>
            </div>
          ))
        )}
        {isLoading && (
          <div style={{ color: 'var(--f1-red)', padding: '10px', fontStyle: 'italic' }}>
            Analyzing telemetry and history...
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <div className="chat-input" style={{ display: 'flex', gap: '10px' }}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Why did Verstappen lose pace on lap 43?"
          style={{
            flexGrow: 1,
            padding: '12px',
            borderRadius: '6px',
            border: '1px solid #444',
            backgroundColor: 'rgba(0,0,0,0.3)',
            color: '#fff',
            fontSize: '1rem'
          }}
          disabled={isLoading}
        />
        <button 
          className="btn-primary" 
          onClick={handleSend}
          disabled={isLoading || !input.trim()}
        >
          {isLoading ? '...' : 'Send'}
        </button>
      </div>
    </div>
  );
}

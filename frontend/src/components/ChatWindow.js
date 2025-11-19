import React from 'react';

function ChatWindow({ messages, input, setInput, onSend }) {
  return (
    <div className="chat-container">
      <div className="messages">
        {messages.map((message, i) => (
          <div key={i} className={`bubble ${message.sender}`}>
            {message.text}
          </div>
        ))}
      </div>
      <form onSubmit={onSend} className="input-form">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
        />
        <button type="submit">Send</button>
      </form>
    </div>
  );
}

export default ChatWindow;

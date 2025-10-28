import React, { useState, useEffect } from "react";
import "./App.css";
import KnowledgeBaseList from "./components/KnowledgeBaseList";
import ChatWindow from "./components/ChatWindow";
import CreateKBDialog from "./components/CreateKBDialog";
import UploadDialog from "./components/UploadDialog";

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [knowledgeBases, setKnowledgeBases] = useState([]);
  const [newKBName, setNewKBName] = useState("");
  const [showKBDialog, setShowKBDialog] = useState(false);
  const [uploadingKB, setUploadingKB] = useState(null);
  const [uploadFile, setUploadFile] = useState(null);

  const API_BASE = "http://localhost:8000";

  useEffect(() => {
    fetchKnowledgeBases();
  }, []);

  const demoKBs = ["finance", "docs"];

  const demoReplies = [
    "That's a great question — in this dataset, the answer seems to suggest...",
    "According to the indexed knowledge base, the relevant document says...",
    "Based on what I found, it looks like...",
  ];

  const fetchKnowledgeBases = async () => {
    try {
      const res = await fetch(`${API_BASE}/knowledge-base/get`);
      if (!res.ok) throw new Error("Fallback to demo data");
      const data = await res.json();
      setKnowledgeBases(data.response.knowledge_bases);
    } catch (err) {
      console.warn("Using demo KBs:", err.message);
      setTimeout(() => setKnowledgeBases(demoKBs), 600);
    }
  };

  const createKnowledgeBase = async (e) => {
    e.preventDefault();
    if (!newKBName.trim()) return;

    try {
      const res = await fetch(`${API_BASE}/knowledge-base/create`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ kb_id: newKBName }),
      });

      if (!res.ok) throw new Error(`Failed to create KB: ${res.statusText}`);
      const data = await res.json();

      alert(`✅ Knowledge Base "${newKBName}" created successfully!`);
      setKnowledgeBases((prev) => [...prev, data.response.kb_id]);
      setNewKBName("");
      setShowKBDialog(false);
    } catch (err) {
      console.error("Error creating KB:", err);
      alert("❌ Failed to create Knowledge Base.");
    }
  };

  const uploadDocument = async (e) => {
    e.preventDefault();
    if (!uploadFile || !uploadingKB) return;

    try {
      const formData = new FormData();
      formData.append("file", uploadFile);
      formData.append("kb_id", uploadingKB);

      const res = await fetch(`${API_BASE}/knowledge-base/document/upload`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error(`Failed to upload: ${res.statusText}`);
      await res.json();

      alert(`✅ File "${uploadFile.name}" uploaded to "${uploadingKB}"`);
      setUploadFile(null);
      setUploadingKB(null);
    } catch (err) {
      console.error("Error uploading file:", err);
      alert("❌ Failed to upload document.");
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = { sender: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    // Simulate latency + fake reply
    setTimeout(() => {
      const botMessage = {
        sender: "bot",
        text:
          demoReplies[Math.floor(Math.random() * demoReplies.length)] +
          " (" +
          new Date().toLocaleTimeString() +
          ")",
      };
      setMessages((prev) => [...prev, botMessage]);
    }, 900);
  };

  return (
    <div className="app-container">
      <div className="app-header">
        <div className="app-header-content">
          <svg
            width="160"
            viewBox="0 0 137 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            className="app-logo"
          >
            <path
              d="M17.5 10L22 0L30.6059 8.60589C31.7939 9.79394 32.388 10.388 32.6105 11.0729C32.8063 11.6755 32.8063 12.3245 32.6105 12.9271C32.388 13.612 31.7939 14.2061 30.6059 15.3941L22 24H15L26.7517 11.3444C27.146 10.9197 27.3432 10.7074 27.3527 10.5263C27.361 10.3691 27.2947 10.2171 27.1739 10.1162C27.0347 10 26.7449 10 26.1654 10H17.5Z"
              fill="currentColor"
            ></path>
            <path
              d="M16.5 14L12 24L3.39411 15.3941C2.20606 14.2061 1.61204 13.612 1.38947 12.9271C1.1937 12.3245 1.1937 11.6755 1.38947 11.0729C1.61204 10.388 2.20606 9.79394 3.39411 8.60589L12 0H19L7.24833 12.6556C6.854 13.0803 6.65684 13.2926 6.6473 13.4737C6.63902 13.6309 6.70527 13.7829 6.82612 13.8838C6.96529 14 7.25505 14 7.83457 14H16.5Z"
              fill="currentColor"
            ></path>
          </svg>
          <h1>RAG Demo</h1>
          <p className="subtitle">LangChain + FastAPI + React + Hatchet</p>
        </div>
      </div>

      <KnowledgeBaseList
        knowledgeBases={knowledgeBases}
        onNewKB={() => setShowKBDialog(true)}
        onUpload={(kbName) => setUploadingKB(kbName)}
      />

      <ChatWindow
        messages={messages}
        input={input}
        setInput={setInput}
        onSend={sendMessage}
      />

      {showKBDialog && (
        <CreateKBDialog
          newKBName={newKBName}
          setNewKBName={setNewKBName}
          onCreate={createKnowledgeBase}
          onClose={() => setShowKBDialog(false)}
        />
      )}

      {uploadingKB && (
        <UploadDialog
          kbName={uploadingKB}
          uploadFile={uploadFile}
          setUploadFile={setUploadFile}
          onUpload={uploadDocument}
          onClose={() => setUploadingKB(null)}
        />
      )}
    </div>
  );
}

export default App;

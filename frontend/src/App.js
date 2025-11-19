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
  const [selectedKB, setSelectedKB] = useState(null);
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
      const res = await fetch(`${API_BASE}/knowledge-bases`);
      if (!res.ok) throw new Error("Fallback to demo data");
      const data = await res.json();
      setKnowledgeBases(data.data.knowledge_bases);
    } catch (err) {
      console.warn("Using demo KBs:", err.message);
      setTimeout(() => setKnowledgeBases(demoKBs), 600);
    }
  };

  const createKnowledgeBase = async (e) => {
    e.preventDefault();
    if (!newKBName.trim()) return;

    try {
      const res = await fetch(`${API_BASE}/knowledge-bases/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ kb_id: newKBName }),
      });

      if (!res.ok) throw new Error(`Failed to create KB: ${res.statusText}`);
      const data = await res.json();

      alert(`✅ Knowledge Base "${newKBName}" created successfully!`);
      setKnowledgeBases((prev) => [...prev, data.data.kb_id]);
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

      const res = await fetch(`${API_BASE}/knowledge-bases/upload`, {
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

    if (!selectedKB) {
      alert("⚠️ Please select a knowledge base first.");
      return;
    }

    const userMessage = { sender: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    try {
      const res = await fetch(`${API_BASE}/chat/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: input,
          kb_id: selectedKB, // ✅ pass selected KB
        }),
      });

      if (!res.ok) throw new Error("Chat request failed");
      const data = await res.json();
      console.log(data);
      const botMessage = {
        sender: "bot",
        text: data.data.response.messages[1],
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      console.error("Chat error:", err);
      // Fallback demo reply
      const botMessage = {
        sender: "bot",
        text:
          demoReplies[Math.floor(Math.random() * demoReplies.length)] +
          ` (demo, KB: ${selectedKB})`,
      };
      setMessages((prev) => [...prev, botMessage]);
    }
  };

  return (
    <div className="app-container">
      <div className="app-header">
        <div className="app-header-content">
          <h1>RAG Demo</h1>
          <p className="subtitle">LangChain + FastAPI + React + Hatchet</p>
        </div>
      </div>

      <KnowledgeBaseList
        knowledgeBases={knowledgeBases}
        selectedKB={selectedKB}
        onSelectKB={setSelectedKB}
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

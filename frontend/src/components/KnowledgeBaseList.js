import React from "react";

function KnowledgeBaseList({ knowledgeBases, onNewKB, onUpload }) {
  return (
    <div className="kb-section">
      <h2>Knowledge Bases</h2>
      <div className="kb-list">
        {knowledgeBases.length ? (
          knowledgeBases.map((kb, i) => (
            <div key={i} className="kb-item">
              <span>📘 {kb}</span>
              <button onClick={() => onUpload(kb)}>Upload Document</button>
            </div>
          ))
        ) : (
          <p className="kb-empty">No knowledge bases yet.</p>
        )}
      </div>
      <button onClick={onNewKB}>+ New Knowledge Base</button>
    </div>
  );
}

export default KnowledgeBaseList;

import React from "react";

function KnowledgeBaseList({
  knowledgeBases,
  selectedKB,
  onSelectKB,
  onNewKB,
  onUpload,
}) {
  return (
    <div className="kb-section">
      <h2>Knowledge Bases</h2>
      <div className="kb-list">
        {knowledgeBases.length ? (
          knowledgeBases.map((kb, i) => (
            <div
              key={i}
              className={`kb-item ${selectedKB === kb ? "selected" : ""}`}
            >
              <span>📘 {kb}</span>
              <div className="kb-actions">
                <button onClick={() => onSelectKB(kb)}>
                  {selectedKB === kb ? "Selected" : "Select"}
                </button>
                <button onClick={() => onUpload(kb)}>Upload Document</button>
              </div>
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

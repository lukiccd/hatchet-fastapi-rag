import React from 'react';

function CreateKBDialog({ newKBName, setNewKBName, onCreate, onClose }) {
  return (
    <div className="dialog-backdrop">
      <div className="dialog">
        <h3>Create Knowledge Base</h3>
        <form onSubmit={onCreate}>
          <input
            type="text"
            value={newKBName}
            onChange={(e) => setNewKBName(e.target.value)}
            placeholder="Knowledge base name..."
          />
          <div className="dialog-buttons">
            <button type="submit">Create</button>
            <button type="button" onClick={onClose}>
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default CreateKBDialog;

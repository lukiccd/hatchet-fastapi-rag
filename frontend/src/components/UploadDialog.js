import React from 'react';

function UploadDialog({ kbName, uploadFile, setUploadFile, onUpload, onClose }) {
  return (
    <div className="dialog-backdrop">
      <div className="dialog">
        <h3>Upload Document to "{kbName}"</h3>
        <form onSubmit={onUpload}>
          <input
            type="file"
            accept=".pdf,.txt,.doc,.docx"
            onChange={(e) => setUploadFile(e.target.files[0])}
          />
          <div className="dialog-buttons">
            <button type="submit">Upload</button>
            <button type="button" onClick={onClose}>
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default UploadDialog;

'use client';

import { useState, useRef, useCallback } from 'react';

export default function UploadSection({ onUploadComplete }) {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [previews, setPreviews] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef(null);

  const handleFiles = useCallback((files) => {
    const fileArray = Array.from(files);
    setSelectedFiles(fileArray);
    setSuccessMsg('');
    setErrorMsg('');

    const newPreviews = fileArray.map((file) => URL.createObjectURL(file));
    setPreviews((prev) => {
      prev.forEach((url) => URL.revokeObjectURL(url));
      return newPreviews;
    });
  }, []);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback(
    (e) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragOver(false);
      if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        handleFiles(e.dataTransfer.files);
      }
    },
    [handleFiles]
  );

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFiles(e.target.files);
    }
  };

  const handleSubmit = async () => {
    if (selectedFiles.length === 0) return;

    setUploading(true);
    setSuccessMsg('');
    setErrorMsg('');

    try {
      const formData = new FormData();
      selectedFiles.forEach((file) => formData.append('files', file));

      const res = await fetch('/api/images/upload', {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => null);
        throw new Error(
          errData?.detail || errData?.message || `Upload failed (${res.status})`
        );
      }

      const data = await res.json();
      const images = Array.isArray(data) ? data : [];
      const totalFaces = images.reduce(
        (sum, img) => sum + (img.face_count || 0),
        0
      );

      setSuccessMsg(
        `Successfully processed ${images.length} image(s) with ${totalFaces} face(s) detected!`
      );
      setSelectedFiles([]);
      setPreviews((prev) => {
        prev.forEach((url) => URL.revokeObjectURL(url));
        return [];
      });
      if (fileInputRef.current) fileInputRef.current.value = '';
      if (onUploadComplete) onUploadComplete();
    } catch (err) {
      setErrorMsg(err.message || 'An unexpected error occurred.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      {/* Dropzone */}
      <div
        className={`dropzone ${isDragOver ? 'drag-over' : ''}`}
        onClick={() => fileInputRef.current?.click()}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') fileInputRef.current?.click();
        }}
      >
        {/* Cloud Upload Icon */}
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="48"
          height="48"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          style={{ color: '#818cf8', marginBottom: '1rem' }}
        >
          <path d="M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242" />
          <path d="M12 12v9" />
          <path d="m16 16-4-4-4 4" />
        </svg>

        <p style={{ fontSize: '1.1rem', fontWeight: 500, marginBottom: '0.25rem' }}>
          Drag &amp; drop images here or click to browse
        </p>
        <p style={{ fontSize: '0.85rem', color: '#94a3b8' }}>
          JPG, PNG, BMP, WEBP
        </p>

        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          multiple
          style={{ display: 'none' }}
          onChange={handleFileChange}
        />
      </div>

      {/* Preview Row */}
      {previews.length > 0 && (
        <div
          style={{
            display: 'flex',
            gap: '0.75rem',
            flexWrap: 'wrap',
            marginTop: '1rem',
          }}
        >
          {previews.map((src, idx) => (
            <div
              key={idx}
              style={{
                width: 72,
                height: 72,
                borderRadius: '0.5rem',
                overflow: 'hidden',
                border: '2px solid rgba(129,140,248,0.4)',
              }}
            >
              <img
                src={src}
                alt={`preview-${idx}`}
                style={{ width: '100%', height: '100%', objectFit: 'cover' }}
              />
            </div>
          ))}
        </div>
      )}

      {/* Submit Button */}
      <button
        className="btn-gradient"
        onClick={handleSubmit}
        disabled={uploading || selectedFiles.length === 0}
        style={{ marginTop: '1.25rem', minWidth: 200 }}
      >
        {uploading ? (
          <>
            <span className="spinner" style={{ marginRight: '0.5rem' }} />
            Processing faces...
          </>
        ) : (
          'Upload & Process'
        )}
      </button>

      {/* Success Message */}
      {successMsg && (
        <p
          style={{
            marginTop: '1rem',
            color: '#4ade80',
            fontWeight: 500,
            fontSize: '0.95rem',
          }}
        >
          {successMsg}
        </p>
      )}

      {/* Error Message */}
      {errorMsg && (
        <p
          style={{
            marginTop: '1rem',
            color: '#f87171',
            fontWeight: 500,
            fontSize: '0.95rem',
          }}
        >
          {errorMsg}
        </p>
      )}
    </div>
  );
}

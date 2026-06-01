'use client';

import { useState, useRef, useCallback } from 'react';

export default function SearchSection() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState('');
  const [searching, setSearching] = useState(false);
  const [results, setResults] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef(null);

  const handleFile = useCallback((file) => {
    setSelectedFile(file);
    setResults(null);
    setErrorMsg('');
    setPreview((prev) => {
      if (prev) URL.revokeObjectURL(prev);
      return URL.createObjectURL(file);
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
        handleFile(e.dataTransfer.files[0]);
      }
    },
    [handleFile]
  );

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFile(e.target.files[0]);
    }
  };

  const handleSearch = async () => {
    if (!selectedFile) return;

    setSearching(true);
    setResults(null);
    setErrorMsg('');

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const res = await fetch('/api/search/by-face', {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => null);
        throw new Error(
          errData?.detail || errData?.message || `Search failed (${res.status})`
        );
      }

      const data = await res.json();
      setResults(data);
    } catch (err) {
      setErrorMsg(err.message || 'An unexpected error occurred.');
    } finally {
      setSearching(false);
    }
  };

  const truncate = (str, len = 24) =>
    str && str.length > len ? str.slice(0, len) + '…' : str;

  return (
    <div>
      <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'flex-start', flexWrap: 'wrap' }}>
        {/* Search Image Preview */}
        {preview && (
          <div
            style={{
              width: 180,
              height: 180,
              borderRadius: '1rem',
              overflow: 'hidden',
              border: '2px solid rgba(52,211,153,0.5)',
              flexShrink: 0,
            }}
          >
            <img
              src={preview}
              alt="Search preview"
              style={{ width: '100%', height: '100%', objectFit: 'cover' }}
            />
          </div>
        )}

        {/* Dropzone */}
        <div style={{ flex: 1, minWidth: 280 }}>
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
            style={{
              borderColor: isDragOver ? '#34d399' : 'rgba(52,211,153,0.35)',
              background: isDragOver
                ? 'rgba(52,211,153,0.08)'
                : 'rgba(52,211,153,0.03)',
            }}
          >
            {/* Face-scan / Magnifying Glass Icon */}
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
              style={{ color: '#34d399', marginBottom: '1rem' }}
            >
              <circle cx="11" cy="11" r="8" />
              <path d="m21 21-4.3-4.3" />
              <circle cx="11" cy="8" r="2" />
              <path d="M7 13.5c0-2 1.5-3.5 4-3.5s4 1.5 4 3.5" />
            </svg>

            <p style={{ fontSize: '1.05rem', fontWeight: 500, marginBottom: '0.25rem' }}>
              Upload a photo to find this person across all images
            </p>
            <p style={{ fontSize: '0.85rem', color: '#94a3b8' }}>
              JPG, PNG, BMP, WEBP
            </p>

            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              style={{ display: 'none' }}
              onChange={handleFileChange}
            />
          </div>

          {/* Search Button */}
          <button
            onClick={handleSearch}
            disabled={searching || !selectedFile}
            style={{
              marginTop: '1.25rem',
              minWidth: 200,
              padding: '0.75rem 1.5rem',
              border: 'none',
              borderRadius: '0.75rem',
              fontWeight: 600,
              fontSize: '1rem',
              color: '#fff',
              cursor: searching || !selectedFile ? 'not-allowed' : 'pointer',
              opacity: searching || !selectedFile ? 0.6 : 1,
              background: 'linear-gradient(135deg, #10b981, #34d399)',
              transition: 'all 0.2s ease',
            }}
          >
            {searching ? (
              <>
                <span className="spinner" style={{ marginRight: '0.5rem' }} />
                Searching...
              </>
            ) : (
              'Search Database'
            )}
          </button>
        </div>
      </div>

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

      {/* Results */}
      {results && (
        <div style={{ marginTop: '2rem' }}>
          {results.results && results.results.length > 0 ? (
            <>
              <p style={{ marginBottom: '1rem', color: '#cbd5e1', fontSize: '0.95rem' }}>
                Found{' '}
                <strong style={{ color: '#34d399' }}>{results.total_matches}</strong>{' '}
                match{results.total_matches !== 1 ? 'es' : ''} across the database
              </p>

              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))',
                  gap: '1.25rem',
                }}
              >
                {results.results.map((result, idx) => (
                  <div
                    key={idx}
                    className="glass-card fade-in"
                    style={{
                      padding: '0.75rem',
                      borderRadius: '1rem',
                      overflow: 'hidden',
                      position: 'relative',
                    }}
                  >
                    {/* Matched Image */}
                    <div
                      style={{
                        width: '100%',
                        aspectRatio: '1',
                        borderRadius: '0.75rem',
                        overflow: 'hidden',
                        marginBottom: '0.75rem',
                      }}
                    >
                      <img
                        src={`/${result.image.stored_filename ? `uploads/originals/${result.image.stored_filename}` : result.image.filepath}`}
                        alt={result.image.original_filename}
                        style={{
                          width: '100%',
                          height: '100%',
                          objectFit: 'cover',
                        }}
                      />
                    </div>

                    {/* Match Badge */}
                    <span className="match-badge">
                      {result.similarity_percent.toFixed(1)}% match
                    </span>

                    {/* Bottom row: face thumbnail + filename */}
                    <div
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        marginTop: '0.5rem',
                      }}
                    >
                      {/* Face Thumbnail Circle */}
                      <div
                        style={{
                          width: 36,
                          height: 36,
                          borderRadius: '50%',
                          overflow: 'hidden',
                          border: '2px solid rgba(52,211,153,0.5)',
                          flexShrink: 0,
                        }}
                      >
                        <img
                          src={`/${result.face.thumbnail_path}`}
                          alt="face"
                          style={{
                            width: '100%',
                            height: '100%',
                            objectFit: 'cover',
                          }}
                        />
                      </div>

                      {/* Filename */}
                      <span
                        style={{
                          fontSize: '0.85rem',
                          color: '#cbd5e1',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap',
                        }}
                        title={result.image.original_filename}
                      >
                        {truncate(result.image.original_filename)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <p
              style={{
                textAlign: 'center',
                color: '#94a3b8',
                fontSize: '1.05rem',
                marginTop: '1.5rem',
              }}
            >
              No matching faces found in the database.
            </p>
          )}
        </div>
      )}
    </div>
  );
}

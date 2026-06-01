"use client";

import { useState, useEffect } from "react";
import Navbar from "../components/Navbar";

export default function GalleryPage() {
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedImage, setSelectedImage] = useState(null);

  useEffect(() => {
    fetchImages();
  }, []);

  async function fetchImages() {
    try {
      const res = await fetch("/api/images?limit=100");
      if (res.ok) {
        const data = await res.json();
        setImages(data);
      }
    } catch (err) {
      console.error("Failed to fetch images:", err);
    } finally {
      setLoading(false);
    }
  }

  async function deleteImage(imageId) {
    if (!confirm("Delete this image and all its detected faces?")) return;
    try {
      const res = await fetch(`/api/images/${imageId}`, { method: "DELETE" });
      if (res.ok) {
        setImages((prev) => prev.filter((img) => img.id !== imageId));
        setSelectedImage(null);
      }
    } catch (err) {
      console.error("Failed to delete image:", err);
    }
  }

  return (
    <>
      <Navbar />
      <main style={{ maxWidth: "1200px", margin: "0 auto", padding: "32px 24px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "32px" }}>
          <div>
            <h1 style={{ fontSize: "28px", fontWeight: 700, color: "var(--text-primary)" }}>
              Image Gallery
            </h1>
            <p style={{ color: "var(--text-secondary)", fontSize: "14px", marginTop: "4px" }}>
              {images.length} image{images.length !== 1 ? "s" : ""} in the database
            </p>
          </div>
        </div>

        {loading ? (
          <div style={{ display: "flex", justifyContent: "center", padding: "80px 0" }}>
            <div className="spinner" style={{ width: "32px", height: "32px", borderWidth: "3px" }} />
          </div>
        ) : images.length === 0 ? (
          <div
            className="glass-card"
            style={{ padding: "80px 24px", textAlign: "center" }}
          >
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--text-muted)" strokeWidth="1.5" style={{ margin: "0 auto 16px" }}>
              <rect x="3" y="3" width="18" height="18" rx="2" />
              <circle cx="8.5" cy="8.5" r="1.5" />
              <path d="m21 15-5-5L5 21" />
            </svg>
            <p style={{ color: "var(--text-secondary)", fontSize: "16px" }}>
              No images uploaded yet
            </p>
            <p style={{ color: "var(--text-muted)", fontSize: "13px", marginTop: "8px" }}>
              Go to the Dashboard to upload your first images
            </p>
          </div>
        ) : (
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))",
              gap: "16px",
            }}
          >
            {images.map((img, i) => (
              <div
                key={img.id}
                className="image-grid-item fade-in"
                style={{ animationDelay: `${i * 0.05}s`, opacity: 0 }}
                onClick={() => setSelectedImage(img)}
              >
                <img
                  src={`/${img.stored_filename ? `uploads/originals/${img.stored_filename}` : img.filepath}`}
                  alt={img.original_filename}
                  loading="lazy"
                />
                <div className="overlay">
                  <div style={{ width: "100%" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "6px", marginBottom: "4px" }}>
                      <span
                        style={{
                          background: "var(--gradient-primary)",
                          color: "white",
                          fontSize: "11px",
                          fontWeight: 600,
                          padding: "2px 8px",
                          borderRadius: "10px",
                        }}
                      >
                        {img.face_count} face{img.face_count !== 1 ? "s" : ""}
                      </span>
                    </div>
                    <p
                      style={{
                        color: "white",
                        fontSize: "12px",
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        whiteSpace: "nowrap",
                      }}
                    >
                      {img.original_filename}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Image Detail Modal */}
        {selectedImage && (
          <div
            style={{
              position: "fixed",
              inset: 0,
              background: "rgba(0,0,0,0.85)",
              zIndex: 100,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              padding: "24px",
              overflowY: "auto",
            }}
            onClick={() => setSelectedImage(null)}
          >
            <div
              className="glass-card fade-in"
              style={{
                maxWidth: "600px",
                width: "100%",
                padding: "24px",
                cursor: "default",
                maxHeight: "90vh",
                overflowY: "auto",
              }}
              onClick={(e) => e.stopPropagation()}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
                <h3 style={{ fontSize: "18px", fontWeight: 600 }}>Image Details</h3>
                <button
                  onClick={() => setSelectedImage(null)}
                  style={{
                    background: "none",
                    border: "none",
                    color: "var(--text-secondary)",
                    cursor: "pointer",
                    fontSize: "20px",
                  }}
                >
                  ✕
                </button>
              </div>
              <div
                style={{
                  width: "100%",
                  maxHeight: "45vh",
                  borderRadius: "12px",
                  overflow: "hidden",
                  marginBottom: "16px",
                  background: "rgba(0,0,0,0.3)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                <img
                  src={`/${selectedImage.stored_filename ? `uploads/originals/${selectedImage.stored_filename}` : selectedImage.filepath}`}
                  alt={selectedImage.original_filename}
                  style={{
                    maxWidth: "100%",
                    maxHeight: "45vh",
                    objectFit: "contain",
                  }}
                />
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px", marginBottom: "16px" }}>
                <div>
                  <p style={{ color: "var(--text-muted)", fontSize: "12px" }}>Filename</p>
                  <p style={{ fontSize: "14px", wordBreak: "break-all" }}>{selectedImage.original_filename}</p>
                </div>
                <div>
                  <p style={{ color: "var(--text-muted)", fontSize: "12px" }}>Faces Detected</p>
                  <p style={{ fontSize: "14px" }}>{selectedImage.face_count}</p>
                </div>
                <div>
                  <p style={{ color: "var(--text-muted)", fontSize: "12px" }}>Uploaded</p>
                  <p style={{ fontSize: "14px" }}>{new Date(selectedImage.uploaded_at).toLocaleDateString()}</p>
                </div>
                <div>
                  <p style={{ color: "var(--text-muted)", fontSize: "12px" }}>Size</p>
                  <p style={{ fontSize: "14px" }}>
                    {selectedImage.file_size ? `${(selectedImage.file_size / 1024).toFixed(1)} KB` : "N/A"}
                  </p>
                </div>
              </div>
              <button
                onClick={() => deleteImage(selectedImage.id)}
                style={{
                  width: "100%",
                  padding: "10px",
                  borderRadius: "10px",
                  border: "1px solid rgba(244, 63, 94, 0.3)",
                  background: "rgba(244, 63, 94, 0.1)",
                  color: "var(--accent-rose)",
                  fontSize: "14px",
                  fontWeight: 500,
                  cursor: "pointer",
                  transition: "all 0.2s ease",
                }}
              >
                Delete Image
              </button>
            </div>
          </div>
        )}
      </main>
    </>
  );
}

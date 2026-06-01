"use client";

import { useState, useEffect } from "react";
import Navbar from "../components/Navbar";

export default function PeoplePage() {
  const [persons, setPersons] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedPerson, setSelectedPerson] = useState(null);
  const [personImages, setPersonImages] = useState([]);
  const [loadingImages, setLoadingImages] = useState(false);
  const [editingName, setEditingName] = useState(false);
  const [nameInput, setNameInput] = useState("");

  useEffect(() => {
    fetchPersons();
  }, []);

  async function fetchPersons() {
    try {
      const res = await fetch("/api/persons?limit=100");
      if (res.ok) {
        const data = await res.json();
        setPersons(data);
      }
    } catch (err) {
      console.error("Failed to fetch persons:", err);
    } finally {
      setLoading(false);
    }
  }

  async function selectPerson(person) {
    setSelectedPerson(person);
    setLoadingImages(true);
    setNameInput(person.name || person.label || "");
    try {
      const res = await fetch(`/api/persons/${person.id}/images`);
      if (res.ok) {
        const data = await res.json();
        setPersonImages(data);
      }
    } catch (err) {
      console.error("Failed to fetch person images:", err);
    } finally {
      setLoadingImages(false);
    }
  }

  async function updateName() {
    if (!selectedPerson || !nameInput.trim()) return;
    try {
      const res = await fetch(`/api/persons/${selectedPerson.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: nameInput.trim() }),
      });
      if (res.ok) {
        const updated = await res.json();
        setSelectedPerson(updated);
        setPersons((prev) =>
          prev.map((p) => (p.id === updated.id ? updated : p))
        );
        setEditingName(false);
      }
    } catch (err) {
      console.error("Failed to update name:", err);
    }
  }

  return (
    <>
      <Navbar />
      <main style={{ maxWidth: "1200px", margin: "0 auto", padding: "32px 24px" }}>
        <div style={{ marginBottom: "32px" }}>
          <h1 style={{ fontSize: "28px", fontWeight: 700, color: "var(--text-primary)" }}>
            Detected People
          </h1>
          <p style={{ color: "var(--text-secondary)", fontSize: "14px", marginTop: "4px" }}>
            {persons.length} unique person{persons.length !== 1 ? "s" : ""} identified
          </p>
        </div>

        {loading ? (
          <div style={{ display: "flex", justifyContent: "center", padding: "80px 0" }}>
            <div className="spinner" style={{ width: "32px", height: "32px", borderWidth: "3px" }} />
          </div>
        ) : persons.length === 0 ? (
          <div className="glass-card" style={{ padding: "80px 24px", textAlign: "center" }}>
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--text-muted)" strokeWidth="1.5" style={{ margin: "0 auto 16px" }}>
              <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
              <circle cx="9" cy="7" r="4" />
              <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
              <path d="M16 3.13a4 4 0 0 1 0 7.75" />
            </svg>
            <p style={{ color: "var(--text-secondary)", fontSize: "16px" }}>
              No people detected yet
            </p>
            <p style={{ color: "var(--text-muted)", fontSize: "13px", marginTop: "8px" }}>
              Upload some photos with faces to get started
            </p>
          </div>
        ) : (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))", gap: "16px" }}>
            {persons.map((person, i) => (
              <div
                key={person.id}
                className="glass-card fade-in"
                style={{
                  padding: "24px",
                  textAlign: "center",
                  cursor: "pointer",
                  animationDelay: `${i * 0.05}s`,
                  opacity: 0,
                }}
                onClick={() => selectPerson(person)}
              >
                {person.thumbnail_path ? (
                  <img
                    src={`/${person.thumbnail_path}`}
                    alt={person.name || person.label || "Person"}
                    style={{
                      width: "72px",
                      height: "72px",
                      borderRadius: "50%",
                      objectFit: "cover",
                      margin: "0 auto 16px",
                      border: "2px solid rgba(99, 102, 241, 0.4)",
                    }}
                  />
                ) : (
                  <div
                    style={{
                      width: "72px",
                      height: "72px",
                      borderRadius: "50%",
                      background: "var(--gradient-primary)",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      margin: "0 auto 16px",
                      fontSize: "28px",
                      fontWeight: 700,
                      color: "white",
                    }}
                  >
                    {(person.name || person.label || "?")[0].toUpperCase()}
                  </div>
                )}
                <p style={{ fontSize: "16px", fontWeight: 600, marginBottom: "4px" }}>
                  {person.name || person.label || "Unknown"}
                </p>
                <p style={{ color: "var(--text-muted)", fontSize: "13px" }}>
                  {person.face_count} appearance{person.face_count !== 1 ? "s" : ""}
                </p>
              </div>
            ))}
          </div>
        )}

        {/* Person Detail Modal */}
        {selectedPerson && (
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
            onClick={() => {
              setSelectedPerson(null);
              setPersonImages([]);
              setEditingName(false);
            }}
          >
            <div
              className="glass-card fade-in"
              style={{ maxWidth: "700px", width: "100%", padding: "28px", cursor: "default", maxHeight: "90vh", overflowY: "auto" }}
              onClick={(e) => e.stopPropagation()}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "24px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
                  {selectedPerson.thumbnail_path ? (
                    <img
                      src={`/${selectedPerson.thumbnail_path}`}
                      alt={selectedPerson.name || selectedPerson.label || "Person"}
                      style={{
                        width: "56px",
                        height: "56px",
                        borderRadius: "50%",
                        objectFit: "cover",
                        flexShrink: 0,
                        border: "2px solid rgba(99, 102, 241, 0.4)",
                      }}
                    />
                  ) : (
                    <div
                      style={{
                        width: "56px",
                        height: "56px",
                        borderRadius: "50%",
                        background: "var(--gradient-primary)",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        fontSize: "22px",
                        fontWeight: 700,
                        color: "white",
                        flexShrink: 0,
                      }}
                    >
                      {(selectedPerson.name || selectedPerson.label || "?")[0].toUpperCase()}
                    </div>
                  )}
                  <div>
                    {editingName ? (
                      <div style={{ display: "flex", gap: "8px" }}>
                        <input
                          value={nameInput}
                          onChange={(e) => setNameInput(e.target.value)}
                          onKeyDown={(e) => e.key === "Enter" && updateName()}
                          autoFocus
                          style={{
                            background: "var(--bg-secondary)",
                            border: "1px solid var(--border-accent)",
                            borderRadius: "8px",
                            padding: "6px 12px",
                            color: "var(--text-primary)",
                            fontSize: "16px",
                            fontWeight: 600,
                            outline: "none",
                          }}
                        />
                        <button className="btn-gradient" style={{ padding: "6px 16px", fontSize: "13px" }} onClick={updateName}>
                          Save
                        </button>
                      </div>
                    ) : (
                      <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                        <h3 style={{ fontSize: "20px", fontWeight: 600 }}>
                          {selectedPerson.name || selectedPerson.label || "Unknown"}
                        </h3>
                        <button
                          onClick={() => setEditingName(true)}
                          style={{
                            background: "none",
                            border: "none",
                            color: "var(--accent-indigo-light)",
                            cursor: "pointer",
                            fontSize: "13px",
                          }}
                        >
                          Edit
                        </button>
                      </div>
                    )}
                    <p style={{ color: "var(--text-muted)", fontSize: "13px", marginTop: "2px" }}>
                      {selectedPerson.face_count} appearance{selectedPerson.face_count !== 1 ? "s" : ""} across {personImages.length} image{personImages.length !== 1 ? "s" : ""}
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => { setSelectedPerson(null); setPersonImages([]); setEditingName(false); }}
                  style={{ background: "none", border: "none", color: "var(--text-secondary)", cursor: "pointer", fontSize: "20px" }}
                >
                  ✕
                </button>
              </div>

              {loadingImages ? (
                <div style={{ display: "flex", justifyContent: "center", padding: "40px 0" }}>
                  <div className="spinner" style={{ width: "28px", height: "28px", borderWidth: "3px" }} />
                </div>
              ) : personImages.length === 0 ? (
                <p style={{ color: "var(--text-muted)", textAlign: "center", padding: "32px" }}>
                  No images found for this person
                </p>
              ) : (
                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(150px, 1fr))", gap: "12px" }}>
                  {personImages.map((img) => (
                    <div key={img.id} className="image-grid-item" style={{ borderRadius: "10px" }}>
                      <img
                        src={`/${img.stored_filename ? `uploads/originals/${img.stored_filename}` : img.filepath}`}
                        alt={img.original_filename}
                        loading="lazy"
                      />
                      <div className="overlay">
                        <p style={{ color: "white", fontSize: "11px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", width: "100%" }}>
                          {img.original_filename}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </main>
    </>
  );
}

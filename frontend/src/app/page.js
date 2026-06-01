"use client";

import { useState, useCallback } from "react";
import Navbar from "./components/Navbar";
import StatsBar from "./components/StatsBar";
import UploadSection from "./components/UploadSection";
import SearchSection from "./components/SearchSection";

export default function Home() {
  const [refreshKey, setRefreshKey] = useState(0);

  const handleUploadComplete = useCallback(() => {
    setRefreshKey((k) => k + 1);
  }, []);

  return (
    <>
      <Navbar />
      <main
        style={{
          maxWidth: "1200px",
          margin: "0 auto",
          padding: "32px 24px",
        }}
      >
        {/* Hero section */}
        <div style={{ textAlign: "center", marginBottom: "48px" }}>
          <h1
            style={{
              fontSize: "clamp(32px, 5vw, 48px)",
              fontWeight: 800,
              lineHeight: 1.1,
              marginBottom: "16px",
              background: "linear-gradient(135deg, #f0f0f5 0%, #8b8b9e 100%)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
            }}
          >
            Intelligent Face
            <br />
            <span
              style={{
                background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
              }}
            >
              Segregation System
            </span>
          </h1>
          <p
            style={{
              fontSize: "16px",
              color: "var(--text-secondary)",
              maxWidth: "520px",
              margin: "0 auto",
              lineHeight: 1.6,
            }}
          >
            Upload your photos and let AI detect, cluster, and organize faces
            automatically. Search for anyone across your entire library
            instantly.
          </p>
        </div>

        {/* Stats */}
        <StatsBar key={refreshKey} />

        {/* Main sections */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 480px), 1fr))",
            gap: "24px",
            marginTop: "32px",
          }}
        >
          <UploadSection onUploadComplete={handleUploadComplete} />
          <SearchSection />
        </div>
      </main>
    </>
  );
}

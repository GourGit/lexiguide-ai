import { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../services/api";

const STAGES = ["Uploading", "Extracting text", "Analyzing clauses", "Scanning risks", "Generating insights", "Complete"];

export default function UploadModal({ open, onClose }) {
  const [dragOver, setDragOver] = useState(false);
  const [stageIndex, setStageIndex] = useState(-1);
  const [error, setError] = useState(null);
  const inputRef = useRef(null);
  const navigate = useNavigate();

  if (!open) return null;

  async function handleFile(file) {
    if (!file) return;
    setError(null);
    setStageIndex(0);
    try {
      const doc = await api.uploadDocument(file);
      setStageIndex(1);
      await new Promise((r) => setTimeout(r, 300));
      setStageIndex(2);
      const result = await api.analyzeDocument(doc.id);
      setStageIndex(4);
      await new Promise((r) => setTimeout(r, 300));
      setStageIndex(5);
      setTimeout(() => navigate(`/documents/${result.document.id}`), 400);
    } catch (err) {
      setError(err.message);
      setStageIndex(-1);
    }
  }

  return (
    <div className="fixed inset-0 bg-ink/40 flex items-center justify-center z-50 p-4">
      <div className="bg-paper rounded-lg max-w-md w-full p-6 shadow-xl border border-line">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-display text-xl text-ink">Analyze a document</h3>
          <button onClick={onClose} className="text-ink-soft hover:text-ink text-xl leading-none">
            ×
          </button>
        </div>

        {stageIndex === -1 && (
          <>
            <div
              onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
              onDrop={(e) => { e.preventDefault(); setDragOver(false); handleFile(e.dataTransfer.files[0]); }}
              onClick={() => inputRef.current?.click()}
              className={`border-2 border-dashed rounded-lg py-12 text-center cursor-pointer transition-colors ${
                dragOver ? "border-accent bg-accent-soft" : "border-line hover:border-accent"
              }`}
            >
              <p className="text-sm text-ink mb-1">Drag & drop a file, or click to browse</p>
              <p className="text-xs text-ink-soft">PDF, DOCX, or TXT · up to 15MB</p>
              <input
                ref={inputRef}
                type="file"
                accept=".pdf,.docx,.txt"
                className="hidden"
                onChange={(e) => handleFile(e.target.files[0])}
              />
            </div>
            {error && <p className="text-sm text-high mt-3">{error}</p>}
          </>
        )}

        {stageIndex >= 0 && (
          <ul className="space-y-3 py-4">
            {STAGES.map((s, i) => (
              <li key={s} className="flex items-center gap-3 text-sm">
                <span
                  className={`w-5 h-5 rounded-full flex items-center justify-center text-xs ${
                    i < stageIndex
                      ? "bg-positive text-white"
                      : i === stageIndex
                      ? "bg-accent text-white animate-pulse"
                      : "bg-paper-dim text-ink-soft"
                  }`}
                >
                  {i < stageIndex ? "✓" : i + 1}
                </span>
                <span className={i <= stageIndex ? "text-ink" : "text-ink-soft"}>{s}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

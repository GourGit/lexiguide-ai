import { useState } from "react";
import Navbar from "../components/Navbar";
import Disclaimer from "../components/Disclaimer";
import ComparisonView from "../components/ComparisonView";
import { api } from "../services/api";

function FileSlot({ label, file, onChange }) {
  return (
    <div>
      <p className="text-xs uppercase tracking-wide text-ink-soft mb-2">{label}</p>
      <label className="block border-2 border-dashed border-line rounded-lg py-10 text-center cursor-pointer hover:border-accent transition-colors">
        <input type="file" accept=".pdf,.docx,.txt" className="hidden" onChange={(e) => onChange(e.target.files[0])} />
        {file ? (
          <span className="text-sm text-ink">{file.name}</span>
        ) : (
          <span className="text-sm text-ink-soft">Click to select a file</span>
        )}
      </label>
    </div>
  );
}

export default function Compare() {
  const [fileA, setFileA] = useState(null);
  const [fileB, setFileB] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function runComparison() {
    if (!fileA || !fileB) return;
    setLoading(true);
    setError(null);
    try {
      const data = await api.compareByFiles(fileA, fileB);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen">
      <Navbar />
      <main className="max-w-5xl mx-auto px-6 py-12">
        <h1 className="font-display text-3xl text-ink mb-2">Compare two documents</h1>
        <p className="text-ink-soft mb-10">
          Upload two versions of the same agreement to see what meaningfully changed.
        </p>

        <div className="grid sm:grid-cols-2 gap-6 mb-6">
          <FileSlot label="Document A" file={fileA} onChange={setFileA} />
          <FileSlot label="Document B" file={fileB} onChange={setFileB} />
        </div>

        <button
          onClick={runComparison}
          disabled={!fileA || !fileB || loading}
          className="bg-accent text-white text-sm font-medium px-6 py-3 rounded-md hover:opacity-90 disabled:opacity-40 transition-opacity"
        >
          {loading ? "Comparing…" : "Explain changes with AI"}
        </button>

        {error && <p className="text-sm text-high mt-4">{error}</p>}

        {result && (
          <div className="rule pt-10 mt-10">
            <ComparisonView comparison={result.comparison} />
          </div>
        )}

        <Disclaimer />
      </main>
    </div>
  );
}

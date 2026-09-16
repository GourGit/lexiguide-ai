import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import UploadModal from "../components/UploadModal";
import StatsBar from "../components/StatsBar";
import { api } from "../services/api";

const QUICK_ACTIONS = [
  { label: "Analyze document", to: null, action: "upload" },
  { label: "Compare documents", to: "/compare" },
  { label: "Try demo", to: null, action: "demo" },
  { label: "Legal information", to: "/legal-info" },
];

export default function Dashboard() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploadOpen, setUploadOpen] = useState(false);
  const [demoLoading, setDemoLoading] = useState(false);
  const [demoError, setDemoError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    api.listDocuments().then(setDocuments).catch(() => {}).finally(() => setLoading(false));
  }, []);

  async function handleAction(action) {
    if (action === "upload") setUploadOpen(true);
    if (action === "demo") {
      setDemoLoading(true);
      setDemoError(null);
      try {
        const doc = await api.loadDemo();
        navigate(`/documents/${doc.id}`);
      } catch (err) {
        setDemoError(err.message || "Could not load demo. Please ensure the backend is running.");
      } finally {
        setDemoLoading(false);
      }
    }
  }

  const analyzed = documents.filter((d) => d.status === "analyzed");

  return (
    <div className="min-h-screen">
      <Navbar />
      <main className="max-w-5xl mx-auto px-6 py-12">
        <h1 className="font-display text-3xl text-ink mb-1">Understand your legal documents with AI.</h1>
        <p className="text-ink-soft mb-10">Upload a document, or explore a sample first.</p>

        <StatsBar />

        <div className="grid sm:grid-cols-4 gap-3 mb-12">
          {QUICK_ACTIONS.map((q) =>
            q.to ? (
              <Link
                key={q.label}
                to={q.to}
                className="border border-line rounded-lg px-4 py-4 text-sm font-medium text-ink hover:border-accent transition-colors text-center"
              >
                {q.label}
              </Link>
            ) : (
              <button
                key={q.label}
                onClick={() => handleAction(q.action)}
                disabled={q.action === "demo" && demoLoading}
                className="border border-line rounded-lg px-4 py-4 text-sm font-medium text-ink hover:border-accent transition-colors text-center disabled:opacity-60 disabled:cursor-not-allowed"
              >
                {q.action === "demo" && demoLoading ? "Loading demo…" : q.label}
              </button>
            )
          )}
        </div>
        {demoError && (
          <p className="text-sm text-high -mt-8 mb-6">{demoError}</p>
        )}

        <div className="rule pt-8">
          <h2 className="font-display text-xl text-ink mb-6">Recent documents</h2>

          {loading && <p className="text-sm text-ink-soft">Loading…</p>}
          {!loading && documents.length === 0 && (
            <p className="text-sm text-ink-soft">
              No documents yet. Analyze one, or try the demo above to explore LexiGuide first.
            </p>
          )}

          <div className="space-y-1">
            {documents.map((d) => (
              <Link
                key={d.id}
                to={`/documents/${d.id}`}
                className="flex items-center justify-between py-4 rule hover:bg-paper-dim/50 -mx-2 px-2 rounded transition-colors"
              >
                <div>
                  <p className="text-sm font-medium text-ink">
                    {d.filename} {d.is_demo && <span className="text-xs text-accent">(Demo)</span>}
                  </p>
                  <p className="text-xs text-ink-soft mt-0.5">
                    {d.document_type || d.file_type.toUpperCase()} · {d.status}
                  </p>
                </div>
                <span className="text-xs text-ink-soft">
                  {new Date(d.created_at).toLocaleDateString()}
                </span>
              </Link>
            ))}
          </div>
        </div>

        {analyzed.length > 0 && (
          <div className="rule pt-8 mt-8">
            <h2 className="font-display text-xl text-ink mb-4">Pending actions</h2>
            <p className="text-sm text-ink-soft">
              Open an analyzed document to review its checklist and generate lawyer-prep questions.
            </p>
          </div>
        )}
      </main>

      <UploadModal open={uploadOpen} onClose={() => setUploadOpen(false)} />
    </div>
  );
}

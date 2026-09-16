import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import Disclaimer from "../components/Disclaimer";
import UploadModal from "../components/UploadModal";
import { api } from "../services/api";

const STEPS = [
  { n: "01", title: "Upload", body: "Add an employment contract, lease, NDA, or any legal document — PDF, Word, or plain text." },
  { n: "02", title: "Understand", body: "Get a plain-language summary, extracted obligations, dates, and financial terms." },
  { n: "03", title: "Review", body: "See an AI Attention Score and clause-by-clause risk findings, each with a suggested question." },
  { n: "04", title: "Take action", body: "Get an action checklist and a ready-to-use summary and question list for a real lawyer." },
];

const FEATURES = [
  { title: "AI Document Analysis", body: "Structured extraction of parties, obligations, dates, and financial terms." },
  { title: "Risk Scanner", body: "Clause-level attention flags — never a verdict, always a reason to look closer." },
  { title: "Contract Comparison", body: "See exactly what changed between two versions of an agreement." },
  { title: "Document Q&A", body: "Ask questions in plain English, grounded in your actual document, with sources cited." },
  { title: "Action Checklist", body: "A concrete list of what to confirm before you sign or act." },
  { title: "Lawyer Preparation", body: "A ready-made summary and question list for your actual consultation." },
];

export default function Landing() {
  const [uploadOpen, setUploadOpen] = useState(false);
  const [demoLoading, setDemoLoading] = useState(false);
  const [demoError, setDemoError] = useState(null);
  const navigate = useNavigate();

  async function tryDemo() {
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

  return (
    <div className="min-h-screen">
      <Navbar />

      <section className="max-w-5xl mx-auto px-6 pt-20 pb-16 text-center">
        <p className="text-xs uppercase tracking-widest text-ink-soft mb-5">GenAI legal document intelligence</p>
        <h1 className="font-display text-4xl sm:text-5xl text-ink leading-tight max-w-3xl mx-auto">
          Legal documents shouldn&rsquo;t require a law degree.
        </h1>
        <p className="text-ink-soft mt-5 max-w-xl mx-auto leading-relaxed">
          LexiGuide AI uses generative AI to explain, compare, and navigate legal documents in
          plain language.
        </p>
        <div className="flex items-center justify-center gap-3 mt-8">
          <button
            onClick={() => setUploadOpen(true)}
            className="bg-accent text-white text-sm font-medium px-6 py-3 rounded-md hover:opacity-90 transition-opacity"
          >
            Analyze a document
          </button>
          <button
            onClick={tryDemo}
            disabled={demoLoading}
            className="border border-line text-ink text-sm font-medium px-6 py-3 rounded-md hover:border-accent transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {demoLoading ? "Loading demo…" : "Try demo"}
          </button>
        </div>
        {demoError && (
          <p className="text-sm text-high mt-3">{demoError}</p>
        )}
      </section>

      <section className="max-w-5xl mx-auto px-6 py-16 rule">
        <h2 className="font-display text-2xl text-ink mb-10">How it works</h2>
        <div className="grid sm:grid-cols-4 gap-8">
          {STEPS.map((s) => (
            <div key={s.n}>
              <p className="font-display text-3xl text-accent mb-2">{s.n}</p>
              <p className="font-medium text-ink mb-1">{s.title}</p>
              <p className="text-sm text-ink-soft leading-relaxed">{s.body}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="max-w-5xl mx-auto px-6 py-16 rule">
        <h2 className="font-display text-2xl text-ink mb-10">Features</h2>
        <div className="grid sm:grid-cols-3 gap-x-8 gap-y-10">
          {FEATURES.map((f) => (
            <div key={f.title}>
              <p className="font-medium text-ink mb-1">{f.title}</p>
              <p className="text-sm text-ink-soft leading-relaxed">{f.body}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="max-w-5xl mx-auto px-6 py-16 rule">
        <h2 className="font-display text-2xl text-ink mb-4">Privacy-first document handling</h2>
        <p className="text-sm text-ink-soft leading-relaxed max-w-2xl">
          Uploaded files are processed to extract structured information and are not exposed
          publicly. Full document text is kept out of the database — only the data needed to
          power analysis, chat, and comparison is stored.
        </p>
      </section>

      <footer className="max-w-5xl mx-auto px-6 py-10">
        <Disclaimer />
      </footer>

      <UploadModal open={uploadOpen} onClose={() => setUploadOpen(false)} />
    </div>
  );
}

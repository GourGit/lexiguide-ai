import { Suspense, lazy } from "react";
import { Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar"; // Assume we might want to show this while loading

// Lazy load route components
const Landing = lazy(() => import("./pages/Landing"));
const Dashboard = lazy(() => import("./pages/Dashboard"));
const DocumentAnalysis = lazy(() => import("./pages/DocumentAnalysis"));
const Compare = lazy(() => import("./pages/Compare"));
const LegalInfo = lazy(() => import("./pages/LegalInfo"));

// Fallback loader
const PageLoader = () => (
  <div className="min-h-screen flex items-center justify-center">
    <p className="text-ink-soft animate-pulse">Loading page...</p>
  </div>
);

export default function App() {
  return (
    <Suspense fallback={<PageLoader />}>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/documents/:id" element={<DocumentAnalysis />} />
        <Route path="/compare" element={<Compare />} />
        <Route path="/legal-info" element={<LegalInfo />} />
        <Route path="*" element={<Landing />} />
      </Routes>
    </Suspense>
  );
}

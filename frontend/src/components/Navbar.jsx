import { Link, NavLink } from "react-router-dom";

const links = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/compare", label: "Compare" },
  { to: "/legal-info", label: "Legal information" },
];

export default function Navbar() {
  return (
    <header className="border-b border-line bg-paper/95 backdrop-blur sticky top-0 z-40">
      <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-baseline gap-2">
          <span className="font-display text-xl text-ink">LexiGuide</span>
          <span className="text-xs text-ink-soft tracking-wide">AI</span>
        </Link>
        <nav className="hidden sm:flex items-center gap-1">
          {links.map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              className={({ isActive }) =>
                `px-3 py-2 text-sm rounded-md transition-colors ${
                  isActive ? "text-ink bg-paper-dim" : "text-ink-soft hover:text-ink"
                }`
              }
            >
              {l.label}
            </NavLink>
          ))}
        </nav>
        <Link
          to="/dashboard"
          className="text-sm font-medium bg-accent text-white px-4 py-2 rounded-md hover:opacity-90 transition-opacity"
        >
          Analyze a document
        </Link>
      </div>
    </header>
  );
}

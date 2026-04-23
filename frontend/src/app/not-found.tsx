import Link from "next/link";
import NavBar from "./components/NavBar";
import Footer from "./components/Footer";
import "./page.css";

export default function NotFound() {
  return (
    <main className="main">
      <NavBar />
      <div className="flex flex-col items-center justify-center min-h-[60vh] px-4">
        <div className="text-center">
          <h1 className="text-6xl font-bold text-gray-800 mb-4">404</h1>
          <h2 className="text-3xl font-semibold text-gray-700 mb-4">Page Not Found</h2>
          <p className="text-gray-600 mb-8 max-w-md">
            The page you're looking for doesn't exist.
          </p>
          <Link
            href="/"
            className="inline-block px-6 py-3 text-white font-semibold rounded-lg transition-colors"
            style={{ backgroundColor: 'var(--orange_highlight)' }}
          >
            Return Home
          </Link>
        </div>
      </div>
      <Footer />
    </main>
  );
}

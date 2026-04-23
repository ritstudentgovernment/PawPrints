import Link from "next/link";
import "./page.css";

export default function Forbidden() {
  return (
    <main className="main">
      <div className="flex flex-col items-center justify-center min-h-[60vh] px-4">
        <div className="text-center">
          <h1 className="text-6xl font-bold text-gray-800 mb-4">401</h1>
          <h2 className="text-3xl font-semibold text-gray-700 mb-4">Unauthorized Access</h2>
          <p className="text-gray-600 mb-8 max-w-md">You are not authorized to access this page.</p>
          <p className="text-gray-600 mb-8 max-w-md">
            Please return to the homepage or contact a Student Government member if you believe this is an error.
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
    </main>
  );
}

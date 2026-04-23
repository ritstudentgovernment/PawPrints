// app/admin/layout.tsx
import "../page.css"; 

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>; // no wrapping, no main, no outer
}

'use client';
import { useEffect } from 'react';
import { useRouter, useSearchParams, usePathname } from 'next/navigation';

export default function LoginErrorAlert() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();

  const hasLoginError = searchParams.get('login_error') === '1';
  const hasNonStudent = searchParams.get('non_student') === '1';
  const hasAlert = hasLoginError || hasNonStudent;

  // Strip the param from the URL once rendered so a refresh doesn't re-show it.
  useEffect(() => {
    if (!hasAlert) return;
    const params = new URLSearchParams(searchParams.toString());
    params.delete('login_error');
    params.delete('non_student');
    const newUrl = params.toString() ? `${pathname}?${params}` : pathname;
    router.replace(newUrl, { scroll: false });
  }, [hasAlert]);

  if (!hasAlert) return null;

  const message = hasNonStudent
    ? 'Sorry, only current RIT students can make a petition or sign them. If you believe this is a mistake, please contact Student Government.'
    : "Login failed. We couldn\u2019t verify your RIT credentials. Please try again or contact Student Government if the problem persists.";

  return (
    <div
      role="alert"
      style={{
        background: '#fef2f2',
        border: '1px solid #fca5a5',
        borderRadius: '0.5rem',
        color: '#991b1b',
        padding: '0.75rem 1.25rem',
        margin: '1rem auto',
        maxWidth: '600px',
        textAlign: 'center',
        fontWeight: 500,
      }}
    >
      {message}
    </div>
  );
}

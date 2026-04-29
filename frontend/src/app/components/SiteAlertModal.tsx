'use client';

import { useEffect, useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogDescription,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { API_URL } from '../api/specialRoute';
import './SiteAlertModal.css';

const SESSION_KEY = 'sg-alert-dismissed';

export default function SiteAlertModal() {
  const alreadyDismissed = typeof window !== 'undefined' && sessionStorage.getItem(SESSION_KEY) === 'true';

  const [open, setOpen] = useState(false);
  const [dismissed, setDismissed] = useState(alreadyDismissed);
  const [message, setMessage] = useState('');

  useEffect(() => {
    const load = async () => {
      try {
        const res = await fetch(`${API_URL}/api/v1/settings/alert`, { credentials: 'include' });
        if (!res.ok) return;
        const data = await res.json();
        if (data.alert_enabled && data.alert_message) {
          setMessage(data.alert_message);
          if (!sessionStorage.getItem(SESSION_KEY)) {
            setOpen(true);
          }
        }
      } catch {
        // silently fail — don't break the page if the endpoint is unreachable
      }
    };
    load();
  }, []);

  const handleDismiss = () => {
    setOpen(false);
    setDismissed(true);
    sessionStorage.setItem(SESSION_KEY, 'true');
  };

  if (!message) return null;

  return (
    <>
      <Dialog open={open} onOpenChange={(v) => { if (!v) handleDismiss(); }}>
        <DialogContent
          onInteractOutside={(e) => e.preventDefault()}
          style={{ maxWidth: '480px' }}
        >
          <DialogHeader>
            <DialogTitle>Notice from Student Government</DialogTitle>
            <DialogDescription asChild>
              <p style={{ marginTop: '0.5rem', color: '#374151', fontSize: '1rem', lineHeight: '1.6' }}>
                {message}
              </p>
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button onClick={handleDismiss}>Dismiss</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {dismissed && (
        <button
          className="site-alert-bell"
          onClick={() => { setOpen(true); setDismissed(false); }}
          title="View SG Notice"
          aria-label="View Student Government notice"
        >
          <span className="material-symbols-outlined site-alert-bell__icon">
            campaign
          </span>
        </button>
      )}
    </>
  );
}

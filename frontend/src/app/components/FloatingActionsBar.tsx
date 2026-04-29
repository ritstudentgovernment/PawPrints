'use client';

import React from 'react';
import './FloatingActionsBar.css';

export default function FloatingActionsBar({ children }: { children: React.ReactNode }) {
  return <div className="floating-actions-bar">{children}</div>;
}

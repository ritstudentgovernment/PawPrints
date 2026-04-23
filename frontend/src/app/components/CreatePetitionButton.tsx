'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import './CreatePetitionButton.css';

const CreatePetitionButton: React.FC = () => {
  const router = useRouter();

  const handleClick = () => {
    // This respects Next.js basePath automatically if you have one.
    router.push('/create');
  };

  return (
    <button
      type="button"
      className="floating-create-button"
      onClick={handleClick}
      aria-label="Create a new petition"
    >
      <span className="material-symbols-outlined floating-create-button__icon">
        add
      </span>
    </button>
  );
};

export default CreatePetitionButton;

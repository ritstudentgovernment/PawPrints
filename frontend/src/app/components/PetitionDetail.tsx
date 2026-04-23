'use client';

import React, { useEffect, useState } from 'react';
import { usePathname, useRouter, useSearchParams } from 'next/navigation';
import './petitiondetail.css';
import { PetitionType } from './Petition';
import SignPetitionButton from './SignButton';
import DOMPurify from 'isomorphic-dompurify';
import { AuthorType, getAuthorName } from '@/types/Author';
import { API_URL } from '../api/specialRoute';
import LexicalViewer from './Petition/LexicalViewer';
import { removeAmp } from './removeAmp';

type UpdateType = {
  id: number;
  message: string;
  created_at: string; // ISO date string
  author_id: string;
  approved_by: string;
  is_draft: boolean;
  is_approved: boolean;
};

type ResponseType = {
  is_response: boolean;
  update: UpdateType;
}

export const dynamic = "force-dynamic";

export default function PetitionDetail({
  p,
  petitionId,
  totalSignatures,
  onSignedChange,
  isOpen,
  onClose,
}: {
  p: PetitionType;
  petitionId: number;
  totalSignatures: number;
  onSignedChange: (id: number, total_signatures: number) => void;
  isOpen: boolean ;
  onClose: () => void;
}) {
  
  const [responses, setResponses] = useState<ResponseType[]>([]);
  const [description, setDescription] = useState<string>("");


  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }

    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);


  useEffect(() => {
    if (!isOpen) return;

    async function fetchUpdates() {
      const url = `${API_URL}/api/v1/petitions/${petitionId}/timeline`;
      const res = await fetch(url, {
        method: "GET",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
      });
      if (!res.ok) {
        return;
      }
      const data = await res.json();

      setResponses(data.petition_updates);
      setDescription(data.petition_description);
    }

    fetchUpdates();
  }, [petitionId]);

  function closeDetail() {
    onClose();
  }

  const handleShare = async () => {
    const shareUrl = `${window.location.origin}/?petition=${p.id}`;

    const shareData = {
      title: p.title,
      text: `Check out this petition on Pawprints: ${p.title}`,
      url: shareUrl,
    };

    if (navigator.share) {
      try {
        await navigator.share(shareData);
      } catch (err) {
        // User cancelled, ignore
      }
    } else {

      await navigator.clipboard.writeText(shareUrl);
      alert("Link copied to clipboard!"); 
    }
  };


  const status = ['Active', 'Charged', 'Responded', 'Expired'][p.status];
  const clean_desc = DOMPurify.sanitize(description, {
    USE_PROFILES: { html: true },
  });

  return (
    <div className={`overlay shadow-sm ${isOpen ? 'open' : ''}`} id={'detail' + p.id} onClick={closeDetail}>
      <div className={`wrapper`} onClick={(e) => e.stopPropagation()}>
        <div className={`header`}>
          <button className={`closebtn`} onClick={closeDetail}>
            <span className="material-symbols-outlined">close</span>
          </button>
          <h2 className={`title`}>{removeAmp(p.title)}</h2>
          <p className={`author`}>{getAuthorName(p.author) ?? "Unknown"}</p>
        </div>
        <div className={'inner'}>
          <div className={`content`}>
            <div className={`description`}>
              <h4>Petition Description</h4>
              <LexicalViewer content={clean_desc} />
            </div>
          </div>

          {p.committee && (
            <div className={`content`}>
              <div className={`description`}>
                <h4>Charged to Committee: {p.committee.name}</h4>
              </div>
            </div>
          )}

          {responses.length > 0 ? (
            responses.map((response, index) => (
              <div className={`response-content`} key={index}>
                <div className={`description`}>
                  <h4>
                    {response.is_response ? 'Petition Response' : 'Petition Update'}
                  </h4>
                  <div className={`update`}>
                    <LexicalViewer content={response.update.message} />
                    <p>
                      <b>Author:</b> {response.update.author_id ?? "Unknown"}
                    </p>
                    <p>
                      <b>Posted At:</b>{' '}
                      {new Date(response.update.created_at).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                      })}
                    </p>
                  </div>
                </div>
              </div>
            ))
          ) : (
            <></>
          )}
        </div>
        <div className={`footer`}>
          <div className={`sign`}>
            <span id={`sign`}>
              <SignPetitionButton
                petitionID={p.id}
                disabled={status === 'Responded'}
                onSignChange={onSignedChange}
              />
            </span>
            <span id={`nums`}>
              <b>{totalSignatures}/200 Signatures</b>
            </span>
          </div>
          <div className={'info'}>
            <div className='info-stats'>
              <span id={`status`}>
                <b>Status:</b> <br />
                {status}
              </span>
              <span id={`submit`}>
                <b>Submitted:</b> <br />
                {new Date(p.created_at).toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                })}
              </span>
              <span id={`expires`}>
                <b>Expires:</b> <br />
                {new Date(p.expires).toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                })}
              </span>
            </div>
            <button onClick={handleShare} className="share-btn icon-only" aria-label="Copy link">
              <span className="material-symbols-outlined">link</span>
              Share
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

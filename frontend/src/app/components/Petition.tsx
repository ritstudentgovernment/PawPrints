'use client';

import { useEffect, useState } from 'react';
import './petition.css';
import dynamic from 'next/dynamic';
import PetitionTag from './PetitionTag';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { useRouter, useSearchParams } from 'next/navigation';
import { AuthorType } from '@/types/Author';
import { API_URL } from '../api/specialRoute';
import { removeAmp } from './removeAmp';
import { useAuth } from '../hooks/useAuth';

const PetitionDetail = dynamic(() => import('./PetitionDetail'), {
  ssr: false,
  loading: () => <p>Loading petition...</p>
});

type TagType = {
  id: number;
  name: string;
  color: string;
  description: string;
  created_at: string;
};

type UpdateType = {
  id: number;
  message: string;
  created_at: string;
  author_id: string;
  approved_by: string;
  is_draft: boolean;
  is_approved: boolean;
};

type CommitteeType = {
  id: number;
  name: string;
  description: string;
};

export type PetitionType = {
  id: number;
  title: string;
  description: string;
  author: AuthorType;
  total_signatures: number;
  created_at: string;
  status: number;
  expires: string;
  has_response: boolean;
  is_draft: boolean;
  response: UpdateType;
  updates: UpdateType[];
  tags?: TagType[];
  committee?: CommitteeType | null; 
};

export default function Petition({
  p
}: {
  p: PetitionType;
}) {
  const router = useRouter();
  const { isAdmin, isCommitteeMember } = useAuth();
  const [tags, setTags] = useState<TagType[]>(p.tags ?? []);

  const status = ['Active', 'Charged', 'Responded', 'Expired'][p.status];
  
  useEffect(() => {
    setTags(p.tags ?? []);
  }, [p.tags]);


  function openDetail() {
    if (isAdmin || isCommitteeMember) {
      router.push(`/review/${p.id}`)
    } else {
      const params = new URLSearchParams(window.location.search);
      params.set('petition', String(p.id));
      router.push(`?${params.toString()}`, { scroll: false });
    }
  }

  function getPetitionStatusColor() {
    switch (status) {
      case 'Responded':
        return 'progressgreen progressbar'
      default:
        return 'progressbar'
    }
  }

  const signaturesRemaining = Math.max(0, 200 - p.total_signatures);
  const percentage = (p.total_signatures / 200) * 100;

  return (
    <div>
      <Card onClick={openDetail} className="petition">
        <CardHeader>
          <progress
            value={p.total_signatures}
            max={200}
            className={getPetitionStatusColor()}
          ></progress>
          <CardDescription>
            {(() => {
              const chargedTo = p.committee ? ` | Charged to ${p.committee.name}` : '';

              if (status === 'Responded') {
                return (
                  <span>
                    <b>{p.total_signatures} Signatures</b> | Responded{chargedTo}
                  </span>
                );
              }

              if (status === 'Expired') {
                return (
                  <span>
                    <b>{p.total_signatures} Signatures</b> | Expired{chargedTo}
                  </span>
                );
              }

              if (status === 'Charged') {
                return (
                  <span>
                    <b>{p.total_signatures} Signatures</b> | Charged{chargedTo}
                  </span>
                );
              }

              if (signaturesRemaining === 0) {
                if (p.updates) {
                  return (
                    <span>
                      <b>{p.total_signatures} Signatures</b> | Updated{chargedTo}
                    </span>
                  );
                }
                return (
                  <span>
                    <b>{p.total_signatures} Signatures</b> | Threshold met{chargedTo}
                  </span>
                );
              }

              return (
                <span>
                  <b>{p.total_signatures} Signatures</b> | Needs {signaturesRemaining} More{chargedTo}
                </span>
              );
            })()}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <CardTitle className="petition-title">{removeAmp(p.title)}</CardTitle>
        </CardContent>
        <CardFooter>
            <div className="tagContainer" style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
              {tags.map((tag) => (
                <PetitionTag
                  key={tag.id}
                  id={tag.id}
                  name={tag.name}
                  description={tag.description}
                  color={tag.color}
                />
              ))}
            </div>
        </CardFooter>
      </Card>
    </div>
  );
}
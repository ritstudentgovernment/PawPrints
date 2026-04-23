'use client';

import React, { useEffect, useMemo, useState } from 'react';
import { API_URL } from '../api/specialRoute';
import { usePathname, useRouter, useSearchParams } from 'next/navigation';
import dynamic from 'next/dynamic';
import type { PetitionType } from './Petition';
import './OwnedPetitionsSection.css';
import { PetitionForm } from '../create/PetitionForm';
import { Button } from '@/components/ui/button';

const PetitionDetail = dynamic(() => import('./PetitionDetail'), {
  ssr: false,
  loading: () => <p>Loading petition...</p>
});

type OwnedPetition = PetitionType & {
  is_draft: boolean;
};

type PageInfo = {
  page: number;
  items: number;
  total_items: number;
  total_pages: number;
};

type ApiResponse = {
  page_info: PageInfo;
  petitions: OwnedPetition[];
};

const EMPTY_PAGE_INFO: PageInfo = {
  page: 1,
  items: 0,
  total_items: 0,
  total_pages: 1,
};

type FilterOption = 'all' | 'draft' | 'petition';

const OwnedPetitionsSection: React.FC = () => {
  const router = useRouter();
  const searchParams = useSearchParams();
  const pathname = usePathname();

  const [petitions, setPetitions] = useState<OwnedPetition[]>([]);
  const [selectedPetitionId, setSelectedPetitionId] = useState<number | null>(null);
  const [isEditing, setIsEditing] = useState<boolean>(false);
  const [pageInfo, setPageInfo] = useState<PageInfo | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isOpen, setIsOpen] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState<number>(1);
  const [filter, setFilter] = useState<FilterOption>('all');

  const safePageInfo = pageInfo ?? EMPTY_PAGE_INFO;

  // Fetch petitions authored by current user (unfiltered: drafts + non-drafts)
  const loadPetitions = async (pageToLoad: number) => {
    setIsLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams();
      params.set('page', pageToLoad.toString());
      params.set('items_per_page', '10');

      const res = await fetch(
        `${API_URL}/api/v1/petitions/user/me?${params.toString()}`,
        {
          credentials: 'include',
        }
      );

      if (!res.ok) {
        setError('Failed to load your petitions.');
        setPetitions([]);
        setPageInfo(null);
        return;
      }

      const data: ApiResponse = await res.json();
      setPetitions(data.petitions || []);
      setPageInfo(data.page_info || EMPTY_PAGE_INFO);
    } catch (err) {
      console.error('Error loading petitions:', err);
      setError('Something went wrong while loading your petitions.');
      setPetitions([]);
      setPageInfo(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadPetitions(page);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page]);

  // Apply client-side filter (All / Petitions / Drafts)
  const visiblePetitions = useMemo(() => {
    if (filter === 'draft') {
      return petitions.filter((p) => p.is_draft);
    }
    if (filter === 'petition') {
      return petitions.filter((p) => !p.is_draft);
    }
    return petitions;
  }, [petitions, filter]);

  const handleFilterChange = (
    event: React.ChangeEvent<HTMLSelectElement>
  ) => {
    const value = event.target.value as FilterOption;
    setFilter(value);
  };

  const goToPreviousPage = () => {
    if (safePageInfo.page > 1) {
      setPage((prev) => prev - 1);
    }
  };

  const goToNextPage = () => {
    if (safePageInfo.page < safePageInfo.total_pages) {
      setPage((prev) => prev + 1);
    }
  };

  const formatDate = (iso: string) => {
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return '—';
    return d.toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  // This uses the same URL pattern as the main Petition card:
  // stays on /profile but sets ?petition=<id>.
  const openDetail = (petitionId: number) => {
    const currentParams = new URLSearchParams(searchParams.toString());
    currentParams.set('petition', petitionId.toString());

    router.push(`${pathname}?${currentParams.toString()}`);

    setSelectedPetitionId(petitionId);
    setIsOpen(true);
  };

  const closeDetail = () => {
    router.push(`${pathname}`, { scroll: false });
    setIsOpen(false);
  }

  const getEmptyMessage = () => {
    if (filter === 'draft') {
      return 'No drafts found for this user.';
    }
    if (filter === 'petition') {
      return 'No petitions found for this user.';
    }
    return 'No petitions found for this user.';
  };

  return (
    <section className="profile-petitions-section">
      <div className="profile-petitions-header">
        <h2>My PawPrints</h2>
        <p>
          These are the petitions you’ve created. Use the filter to view drafts
          or published petitions and click “View details” to open the full
          petition.
        </p>
      </div>

      <div className="profile-petitions-controls">
        <label htmlFor="petition-filter" className="profile-petitions-label">
          Filter:
        </label>
        <select
          id="petition-filter"
          className="profile-petitions-select"
          value={filter}
          onChange={handleFilterChange}
        >
          <option value="all">All</option>
          <option value="petition">Petitions</option>
          <option value="draft">Drafts</option>
        </select>
      </div>

      <div className="profile-petitions-card">
        {isLoading ? (
          <div className="profile-petitions-loading">
            Loading your petitions…
          </div>
        ) : error ? (
          <div className="profile-petitions-error">{error}</div>
        ) : visiblePetitions.length === 0 ? (
          <div className="profile-petitions-empty">{getEmptyMessage()}</div>
        ) : (
          <>
            <div className="profile-petitions-table-wrapper">
              <table className="profile-petitions-table">
                <thead>
                  <tr>
                    <th>Title</th>
                    <th>Created</th>
                    <th>Expires</th>
                    <th>Signatures</th>
                    <th>Type</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {visiblePetitions.map((p) => (
                    <tr key={p.id}>
                      <td className="profile-petitions-title-cell" data-label="Title">
                        <span className="profile-petitions-title">{p.title}</span>
                      </td>
                      <td data-label="Created">{formatDate(p.created_at)}</td>
                      <td data-label="Expires">{formatDate(p.expires)}</td>
                      <td data-label="Signatures">{p.total_signatures}</td>
                      <td data-label="Type">
                        {p.is_draft ? (
                          <span className="profile-pill profile-pill-draft">Draft</span>
                        ) : (
                          <span className="profile-pill profile-pill-petition">Petition</span>
                        )}
                      </td>
                      <td className="profile-petitions-actions-cell" data-label="">
                        <button
                          type="button"
                          className="profile-petitions-view-button"
                          onClick={() => openDetail(p.id)}
                        >
                          View details
                        </button>
                      </td>

                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="profile-petitions-pagination">
              <button
                type="button"
                onClick={goToPreviousPage}
                disabled={safePageInfo.page <= 1 || isLoading}
              >
                Previous
              </button>
              <span className="profile-petitions-page-info">
                Page {safePageInfo.page} of {safePageInfo.total_pages}
              </span>
              <button
                type="button"
                onClick={goToNextPage}
                disabled={
                  safePageInfo.page >= safePageInfo.total_pages || isLoading
                }
              >
                Next
              </button>
            </div>
          </>
        )}
      </div>

      {/* TODO: FIX EDIT PETITION FORM, ADD INITIAL DATA TO <PetitionForm /> */}
      

      {/* Render PetitionDetail modals for each visible petition.
          PetitionDetail will decide whether to open based on the
          ?petition=<id> query param, just like on the main browse page. */}
      {visiblePetitions.map((p: any) => (
      selectedPetitionId === p.id && (
        /* Check if we should show the Form or the Detail */
        p.is_draft ? (
          <div className="form">
          <Button onClick={() => {setSelectedPetitionId(null)}} className="close-form">Close</Button>
          <PetitionForm
            key={`edit-${p.id}`}
            init_is_edit={true}
            init_petition_id={p.id}
            init_title={p.title}
            init_tags={p.tags?.map((t: { name: string, id: number }) => (t.name, t.id)) ?? []}
          />
          </div>
        ) : (
          <PetitionDetail
            key={p.id}
            p={p}
            petitionId={p.id}
            totalSignatures={p.total_signatures}
            isOpen={isOpen}
            // Pass a prop to PetitionDetail to trigger the edit mode
            onSignedChange={() => {}}
            onClose={closeDetail}
          />
        )
      )
    ))}
    </section>
  );
};

export default OwnedPetitionsSection;

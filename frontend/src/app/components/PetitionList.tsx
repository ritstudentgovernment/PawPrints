'use client'
import { useState, useEffect, useCallback, useRef } from 'react';
import Petition, { PetitionType } from './Petition';
import './petitioncontainer.css';
import PetitionEmpty from './PetitionEmpty';
import PetitionDetail from './PetitionDetail';
import { API_URL, GET, GETTag } from '../api/specialRoute';
import Loading from './loading';
import { useSearchParams, useRouter } from 'next/navigation';
import { useAuth } from '../hooks/useAuth';
import { sleep } from './loadBuffer';



export default function PetitionList({
    initialData,
    query,
    tag,
    status
}: {
    initialData: PetitionType[];
    query?: string;
    tag?: string;
    status ?: string;
}) {
    const [petitions, setPetitions] = useState(initialData);
    const [page, setPage] = useState(2);
    const [itemsPerPage] = useState(40);
    const [hasMore, setHasMore] = useState(true);
    const [openPetition, setOpenPetition] = useState<PetitionType | null>(null);
    const fetchInProgress = useRef(false);
    const searchParams = useSearchParams();
    const router = useRouter();
    const openPetitionId = searchParams.get('petition');
    const prevSearchRef = useRef<string | null>(null);


    useEffect(() => {
        if (petitions != undefined && petitions.length > 0) {
            // Save petitions and page state to sessionStorage when they change
            sessionStorage.setItem("petitions", JSON.stringify(petitions));
            sessionStorage.setItem("page", page.toString());
        }
    }, [petitions, page]);

    // TODO: FIX THIS, DOUBLE FETCHING ISSUE FOR FIRST LOAD ON PETITIONS 

    useEffect(() => {
        const current = searchParams.toString();
        const prev = prevSearchRef.current;

        prevSearchRef.current = current;

        if (!prev) return;

        const currParams = new URLSearchParams(current);
        const prevParams = new URLSearchParams(prev);

        currParams.delete('petition');
        prevParams.delete('petition');

        // only petition param changed - no need to refetch
        if (currParams.toString() === prevParams.toString()) {
            return;
        }

        const statusParam = searchParams.get('status') || undefined; // Get the current 'status' param
        const queryParam = searchParams.get('query') || undefined; // Get the current 'query' param
        const tagParam = searchParams.get('tag') || undefined;

        const fetchNewStatus = async () => {
            const result = await GET(queryParam, statusParam, tagParam, 1, itemsPerPage);
            setPetitions(result.petitions || []);
        }
        fetchNewStatus();

        // Check if the 'petition' param is the only one that changes
        // If other parameters change (excluding 'petition'), reset the page and petitions
        const queryString = searchParams.toString();
        if (!queryString.includes('petition')) {
            setPage(1); 
            setPetitions(initialData); // Clear petitions
        }
    }, [searchParams]);


    const fetchMorePetitions = useCallback(async () => {
        if (fetchInProgress.current || !hasMore) return;

        try {
            fetchInProgress.current = true;
            const result = await GET(query, status, tag, page, itemsPerPage);
            const data = result.petitions || [];

            if (data.length === 0) {
                setHasMore(false);
                fetchInProgress.current = false;
            } else {
                setPetitions(prev => [...prev, ...data]);
                setPage(prev => prev + 1);
            }
            await sleep(500);
        } catch (error) {
            console.error('Error fetching more petitions:', error);
        } finally {
            fetchInProgress.current = false;
        }
    }, [tag, query, status, page, itemsPerPage, hasMore]);

    useEffect(() => {
        async function refetch() {
            setPage(1);
            setHasMore(true);

            if (tag) {
            const res = await GETTag(tag, 1, itemsPerPage);
            setPetitions(res.petitions || []);
            }
        }

        refetch();
    }, [tag]);

    useEffect(() => {
        async function loadPetition() {
            if (!openPetitionId) {
            setOpenPetition(null);
            return;
            }

            const id = Number(openPetitionId);

            // check if already in list
            const existing = petitions.find(p => p.id === id);
            if (existing) {
            setOpenPetition(existing);
            return;
            }

            // otherwise fetch directly
            const res = await fetch(`${API_URL}/api/v1/petitions/${id}`, {
            credentials: 'include'
            });
            const data = await res.json();
            setOpenPetition(data);
        }

        loadPetition();
    }, [openPetitionId, petitions]);


    const handleScroll = useCallback(() => {
        if (
            window.innerHeight + document.documentElement.scrollTop >=
            document.documentElement.offsetHeight - 5
        ) {
            fetchMorePetitions();
        }
    }, [fetchMorePetitions]);

    useEffect(() => {
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, [handleScroll]);

    const handleSignatureUpdate = useCallback((id: number, newCount: number) => {
        setPetitions(prevPetitions => 
            prevPetitions.map(p => 
                p.id === id ? { ...p, total_signatures: newCount } : p
            )
        );

        setOpenPetition(prev => 
            (prev && prev.id === id) 
                ? { ...prev, total_signatures: newCount } 
                : prev
        );
    }, []);

    try {
        
        return (
            <>
            <div className="petitions-container">
                {petitions.length > 0 ? (
                    petitions.map((petition: PetitionType, index: number) => (
                        <Petition key={`${index}-${petition.id}`} p={petition}/>
                    ))
                ) : (
                    <PetitionEmpty />
                )}
                {openPetition && (
                <PetitionDetail
                    p={openPetition}
                    petitionId={openPetition.id}
                    totalSignatures={openPetition.total_signatures}
                    onSignedChange={handleSignatureUpdate}
                    isOpen={true}
                    onClose={() => {
                        const params = new URLSearchParams(window.location.search);
                        params.delete('petition');
                        router.push(`?${params.toString()}`, { scroll: false });
                    }}
                />
                )}
            </div>
                {fetchInProgress.current && <div className="loader-container"><Loading /></div>}
            </>
        );
    } catch (e) {
        console.log(e);
        return <PetitionEmpty />;
    }
}

import React, { Suspense } from 'react';
import NavBar from './components/NavBar';
import ClearFilterButton from './components/clearFilterButton';
import PetitionContainer from './components/PetitionContainer';
import Search from './components/Search';
import './page.css';
import Loading from './components/loading';
import Footer from './components/Footer';
import { API_URL } from './api/specialRoute';
import StatusButtons from './components/statusButtons';
import Banner from './components/Banner';
import CreatePetitionButton from './components/CreatePetitionButton';
import LoginErrorAlert from './components/LoginErrorAlert';
import SiteAlertModal from './components/SiteAlertModal';
import FloatingActionsBar from './components/FloatingActionsBar';

import { Metadata, ResolvingMetadata } from "next";

// define props for the Server Component
type Props = {
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
};

export async function generateMetadata(
  { searchParams }: Props,
  parent: ResolvingMetadata
): Promise<Metadata> {
  // Grab ID from URL (e.g. ?petition=4624)
  const resolvedSearchParams = await searchParams; 
  const petitionId = resolvedSearchParams.petition;

  // If ID exists, fetch data purely for the <meta> tags
  if (petitionId) {
    try {
      const res = await fetch(`${API_URL}/api/v1/petitions/${petitionId}`);
      if (res.ok) {
        const data = await res.json();
        return {
          title: `Sign this Petition!`,
          description: data.title.length > 200 ? data.title.substring(0, 200) + "..." : data.title,
          // FOR IMAGES LATER
          // openGraph: {
          //   images: [data.image_url || "/default-share.png"],
          // },
        };
      }
    } catch (e) {
      console.error(`Error fetching petitions: ${e}`)
    }
  }

  // Fallback if no petition selected
  return {
    title: "Pawprints",
    description: "Start or sign a petition today.",
  };
}

export default async function Home({searchParams}: Props) {
  // Unwrap searchParams (server-side)
  const params = await searchParams;
  const query = Array.isArray(params.query) ? params.query[0] : params.query || '';
  const currentPage = Number(Array.isArray(params.page) ? params.page[0] : params.page) || 1;
  const tag = Array.isArray(params.tag) ? params.tag[0] : params.tag || '';
  const status = Array.isArray(params.status) ? params.status[0] : params.status || '';

  return (
    <main className="main">
      <NavBar />
      <Banner />

      <div className="outer">
        <Suspense fallback={null}>
          <LoginErrorAlert />
        </Suspense>
        <Search placeholder="Search petitions..." />
        <StatusButtons />
        <Suspense key={currentPage} fallback={<Loading />}>
          <PetitionContainer query={query} tag={tag} status={status} />
        </Suspense>
      </div>

      <FloatingActionsBar>
        <SiteAlertModal />
        <CreatePetitionButton />
      </FloatingActionsBar>
    </main>
  );
}
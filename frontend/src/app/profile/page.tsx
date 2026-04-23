'use client';

import { API_URL } from "../api/specialRoute";
import Footer from "../components/Footer";
import NavBar from "../components/NavBar";
import "./page.css";
import Profile from "../components/profile";
import OwnedPetitionsSection from "../components/OwnedPetitionsSection";
import { Suspense } from "react";

export const dynamic = "force-dynamic";

export default function Page() {
  return (
    <main className="main">
      <NavBar />
      <div className="profile-page-outer">
        <div className="profile-layout">
          <section className="profile-layout-left">
            <Profile />
          </section>
          <section className="profile-layout-right">
            <Suspense fallback={<div>Loading...</div>}>
              <OwnedPetitionsSection />
            </Suspense>
          </section>
        </div>
      </div>
      <Footer />
    </main>
  );
}

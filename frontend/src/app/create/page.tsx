'use client';

import Footer from "../components/Footer";
import NavBar from "../components/NavBar";
import BannerCreate from "../components/BannerCreate";
import './page.css';
import { PetitionForm } from "./PetitionForm";
import { useAuth } from "../hooks/useAuth";
  
export default function Create() {

    const { isLoggedIn } = useAuth();

    if (!isLoggedIn) {
      return (
        <main className={`main`}>
          <NavBar/>
          <BannerCreate></BannerCreate>
            <div className={`outercreate`}>
                  <h1>Please Log In</h1>
                  <p>You must be logged in to create a petition.</p>
            </div>
      <Footer/>

    </main>
      )
    }

    return (
    <main className={`main`}>
          <NavBar/>
          <BannerCreate></BannerCreate>
            <div className={`outercreate`}>
                  <h1>Instructions</h1>
                  <p>Below, fill out each field and either save your changes as a draft, or publish your petition!</p>
                      
                  <h2>Petition Title</h2> 
                  <p>Make sure your title is action-oriented and preferably a one-line statement that summarizes your petition.</p>
                      
                  <h2>Petition Description</h2>
                  <p>This is the explanation and reasoning behind your petition. Why should someone sign it? How will it improve the community?</p>
                      
                  <h2>Petition Tags</h2>
                  <p>Tags will help others understand what the petition is about.</p>

                  <h2>Please Remember</h2>
                  <p>If this petition is about another person, staff, or faculty member, talk to the <b>Ombuds</b> office instead.</p>

                  <h1>Your Petition</h1>
                <div className="form-container">
                  <PetitionForm></PetitionForm>
                </div>

            </div>
      <Footer/>

    </main>
    )
}
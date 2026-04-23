// 'use client';

// import React, { useEffect, useState } from 'react';
// import { usePathname, useRouter, useSearchParams } from 'next/navigation';
// // import './petitiondetail.css';
// import { PetitionType } from './Petition';
// import SignPetitionButton from './SignButton';
// import DOMPurify from "isomorphic-dompurify";
// import { getAuthorName } from '@/types/Author';

// export default function PetitionDetail({ p, isLoggedIn, onSign }: { p: PetitionType; isLoggedIn: boolean; onSign: () => void }) {
//     const searchParams = useSearchParams();
//     const router = useRouter();
//     const pathname = usePathname();


//     // Handle showing the modal based on the current query
//     useEffect(() => {
//         const petitionId = searchParams.get('petition');
//         const detail = document.getElementById(`detail${petitionId}`);
//         const mainElement = document.querySelector('main');

//         if (petitionId) {
//             if (detail) {
//                 detail.style.display = 'block';
//                 detail.style.opacity = '1';
//             }
//             mainElement!.classList.add('no-scroll'); // Add a class to prevent scrolling

//         } else {
//             if (detail) {
//                 detail.style.display = 'none';
//                 detail.style.opacity = '0';
//             }
//             mainElement!.classList.remove('no-scroll'); // Remove the class to restore scrolling
//         }
//     }, [searchParams]);

//     // Close the modal and remove the query param
//     function closeDetail() {
//         const currentParams = new URLSearchParams(searchParams.toString());
//         currentParams.delete('petition'); // Remove the petition parameter

//         // Update the URL without redirecting to the home page
//         router.replace(`${pathname}?${currentParams.toString()}`);

//         const detail = document.getElementById(`detail${p.id}`);
//         if (detail) {
//             detail.style.display = 'none';
//             detail.style.opacity = '0';
//         }
//     }

//     const status = ['Active', 'Charged', 'Responded', 'Expired'][p.status];
//     const clean_desc = DOMPurify.sanitize(p.description, { USE_PROFILES: { html: true } });

//     const getAuthorName = (a: any) => {
//         if (!a) return '';
//         if (typeof a === 'string') return a;
//         if (typeof a === 'object') {
//             const fn = a.first_name ?? a.firstName ?? '';
//             const ln = a.last_name ?? a.lastName ?? '';
//             const username = a.username ?? a.user ?? '';
//             if (fn || ln) return `${fn} ${ln}`.trim();
//             return username || '';
//         }
//         return String(a);
//     };

//     return (
//         <div className={`overlay shadow-sm`} id={"detail" + p.id}>
//             <div className={`wrapper`}>
//                 <div className={`header`}>
//                     <button className={`closebtn`} onClick={closeDetail}>
//                         <span className="material-symbols-outlined">close</span>
//                     </button>
//                     <h2 className={`title`}>
//                         {p.title}
//                     </h2>
//                     <p className={`author`}>
//                         {getAuthorName(p.author)}
//                     </p>
//                 </div>
//                 <div className={'inner'}>
//                     <div className={`content`}>
//                         {/* maybe convert this to another component */}

//                         <div className={`description`}>
//                             <h4>
//                                 Petition Description
//                             </h4>

//                             <div className={'innerDesc'} dangerouslySetInnerHTML={{ __html: clean_desc }} />
//                         </div>

//                     </div>
//                     {p.updates.length > 0 ? (
//                         p.updates.map((update, index) => (
//                             <div className={`response-content`}>
//                                 <div className={`description`}>
//                                     <h4>{update.is_response ? 'Petition Response' : 'Petition Update'}</h4>

//                                     <div key={index} className={`update`}>
//                                         <div className={'innerDesc'} dangerouslySetInnerHTML={{ __html: update.message }} />
//                                         <p><b>Author:</b> {getAuthorName(update.author)}</p>
//                                         <p><b>Posted At:</b> {new Date(update.created_at).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}</p>

//                                     </div>
//                                 </div>
//                             </div>
//                         ))
//                     ) : (<></>)}
//                 </div>

//                 <div className={`footer`}>
//                     <div className={`sign`}>
//                         {/* <button id={`sign`} ><b>Sign this petition</b></button> */}
//                         <span id={`sign`}><SignPetitionButton petitionID={p.id} onSign={onSign}></SignPetitionButton></span>
//                         <span id={`nums`}><b>{p.total_signatures}/200 Signatures</b></span>
//                     </div>
//                     <div className={'info'}>
//                         {/*possible report thing?*/}
//                         <span></span>
//                         <span id={`status`}><b>Status:</b> <br />{status}</span>
//                         <span id={`submit`}><b>Submitted:</b> <br />
//                             {new Date(p.created_at).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}</span>
//                         <span id={`expires`}><b>Expires:</b> <br />
//                             {new Date(p.expires).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}</span>
//                     </div>
//                 </div>
//             </div>
//         </div>
//     )
// }
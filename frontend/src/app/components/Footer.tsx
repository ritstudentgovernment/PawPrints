'use client'
import React from 'react'
import Link from 'next/link'
import logo from '../assets/pawprintslogowhite-03.svg'
import './footer.css'

export default function Footer() {
    return (
        <div className={"footer-content"}>
            <div className={"footer-grid"}>
                <div className={"footer-section"}>
                    <ul>
                        <li><Link href={"/create"}>Create</Link></li>
                        <li><Link href={"/"}>Browse</Link></li>
                        <li><Link href={"/about"}>About</Link></li>
                        <li><Link href={"/committees"}>Committees</Link></li>
                        <li><Link href={"https://www.rit.edu/studentgovernment/"}>SG Website</Link></li>
                    </ul>
                </div>
                
                <div className={"footer-logo"}>
                    <Link href={"/"}>
                        <img src={logo.src} alt="PawPrints Logo" />
                    </Link>
                </div>
            </div>
        </div>
    )
}
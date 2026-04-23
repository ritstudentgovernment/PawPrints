
'use client';
import React from 'react';
import './loginbutton.css';
import Link from 'next/link';
import { useAuth } from '../hooks/useAuth';

export default function LoginButton() {
    const { isLoggedIn, user, isAdmin, logIn } = useAuth();



    if (!isLoggedIn) {
        return (
            <button className="login-btn" onClick={() => logIn()}>
                <span className='login-text'>LOGIN</span>
                <span className="login-icon material-symbols-outlined">
                    account_circle
                </span>
            </button>
        );
    } else {
        return (
            <div>
                <Link className="profile-link" href={isAdmin ? "/admin" : "/profile"}>
                    <span className="login-text">
                        Welcome, {user?.first_name}!
                    </span>
                    <span className="login-icon material-symbols-outlined">
                        account_circle
                    </span>
                </Link>
            </div>
        );
    }
}

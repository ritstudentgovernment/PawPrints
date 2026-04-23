
'use client';
import React from 'react';
import './profile.css';
import Link from 'next/link';
import { useAuth } from '../hooks/useAuth';

export const dynamic = "force-dynamic";

export default function Profile() {
    const { user, logOut } = useAuth();

    if (!user) {
        return (
            <div>
                <h1 className="profile-title">User Profile</h1>
                <p>You are not logged in. Please login to view your profile.</p>
            </div>
        );
    }
    return (
        <div className="profile-container">
            <h1 className="profile-title">User Profile</h1>
            <div className="profile-info">
                <p><strong>First Name:</strong> {user?.first_name}</p>
                <p><strong>Last Name:</strong> {user?.last_name}</p>
                <p><strong>Username:</strong> {user?.username}</p>
                <p><strong>Email:</strong> {user?.username + "@rit.edu"}</p>
            </div>
            <br/>
            <button className="logout-btn" onClick={logOut}>
                LOGOUT
            </button>
        </div>
        
    );
}

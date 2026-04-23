"use client";

import NavBar from "../components/NavBar";
import Footer from "../components/Footer";
import "./admin.css";
import AdminUsersSection from "./AdminUsersSection";
import AdminRolesSection from "./AdminRolesSection";
import AdminPermissionsSection from "./AdminPermissionsSection";
import AdminCommitteesSection from "./AdminCommitteesSection";
import AdminPetitionsSection from "./AdminPetitionsSection";
import AdminTagsSection from "./AdminTagsSection";
import AdminPawstatsSection from "./AdminPawstatsSection";
import { useState } from "react";
import "material-symbols";
import { useAuth } from "../hooks/useAuth";
import Forbidden from "../forbidden";

export default function AdminPage() {
  const [activeTab, setActiveTab] = useState("users");
  const { isAdmin } = useAuth();

  const handleNavClick = (tab: string) => {
    setActiveTab(tab);
  };

  if (!isAdmin) {
    return (
      <main className="main">
        <NavBar />
          <Forbidden />
        <Footer />
      </main>
    )
  }

  return (
      <main className="main">
        <NavBar />

        <div className="admin-container">
          {/* Vertical Sidebar Navigation */}
          <aside className="admin-vertical-nav">
            <div className="admin-nav-header">
              <h2>Admin Panel</h2>
            </div>
            <nav className="admin-nav-list">
              <button
                className={`admin-nav-item ${activeTab === "users" ? "active" : ""}`}
                onClick={() => handleNavClick("users")}
              >
                <span className="material-symbols-outlined" aria-hidden="true">group</span>
                Users
              </button>
              <button
                className={`admin-nav-item ${activeTab === "roles" ? "active" : ""}`}
                onClick={() => handleNavClick("roles")}
              >
                <span className="material-symbols-outlined" aria-hidden="true">badge</span>
                Roles
              </button>
              <button
                className={`admin-nav-item ${activeTab === "permissions" ? "active" : ""}`}
                onClick={() => handleNavClick("permissions")}
              >
                <span className="material-symbols-outlined" aria-hidden="true">lock</span>
                Permissions
              </button>
              <button
                className={`admin-nav-item ${activeTab === "committees" ? "active" : ""}`}
                onClick={() => handleNavClick("committees")}
              >
                <span className="material-symbols-outlined" aria-hidden="true">people</span>
                Committees
              </button>
              <button
                className={`admin-nav-item ${activeTab === "petitions" ? "active" : ""}`}
                onClick={() => handleNavClick("petitions")}
              >
                <span className="material-symbols-outlined" aria-hidden="true">description</span>
                Petitions
              </button>
              <button
                className={`admin-nav-item ${activeTab === "tags" ? "active" : ""}`}
                onClick={() => handleNavClick("tags")}
              >
                <span className="material-symbols-outlined" aria-hidden="true">label</span>
                Tags
              </button>
              <button
                className={`admin-nav-item ${activeTab === "pawstats" ? "active" : ""}`}
                onClick={() => handleNavClick("pawstats")}
              >
                <span className="material-symbols-outlined" aria-hidden="true">bar_chart</span>
                Pawstats
              </button>
            </nav>
          </aside>

          {/* Main Content */}
          <div className="admin-content">
            <header className="admin-header">
              <h1 className="admin-title">Admin Dashboard</h1>
              <p className="admin-subtitle">
                Manage users, roles, permissions, and committees from a single place.
              </p>
            </header>

            {/* USERS SECTION */}
            {activeTab === "users" && (
              <section id="users" className="admin-section">
                <AdminUsersSection />
              </section>
            )}

            {/* ROLES SECTION */}
            {activeTab === "roles" && (
              <section id="roles" className="admin-section">
                <AdminRolesSection />
              </section>
            )}

            {/* PERMISSIONS SECTION */}
            {activeTab === "permissions" && (
              <section id="permissions" className="admin-section">
                <AdminPermissionsSection />
              </section>
            )}

            {/* COMMITTEES SECTION */}
            {activeTab === "committees" && (
              <section id="committees" className="admin-section">
                <AdminCommitteesSection />
              </section>
            )}

            {/* PETITIONS SECTION */}
            {activeTab === "petitions" && (
              <section id="petitions" className="admin-section">
                <AdminPetitionsSection />
              </section>
            )}

            {/* TAGS SECTION */}
            {activeTab === "tags" && (
              <section id="tags" className="admin-section">
                <AdminTagsSection />
              </section>
            )}

            {/* PAWSTATS SECTION */}
            {activeTab === "pawstats" && (
              <section id="pawstats" className="admin-section">
                <AdminPawstatsSection />
              </section>
            )}
          </div>
        </div>

        <Footer />
      </main>
  );
}

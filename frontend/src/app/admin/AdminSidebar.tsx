"use client";
import "./admin.css";

export default function AdminSidebar() {

    const scrollToSection = (id: string) => {
        const element = document.getElementById(id);
        if (element) {
            element.scrollIntoView({ behavior: "smooth", block: "start" });
        }
    };

    return (
        <div className="admin-sidebar">
            <h2>Admin Panel</h2>

            <ul>
                <li onClick={() => scrollToSection("users")}>Users</li>
                <li onClick={() => scrollToSection("roles")}>Roles</li>
                <li onClick={() => scrollToSection("permissions")}>Permissions</li>
                <li onClick={() => scrollToSection("committees")}>Committees</li>
                <li onClick={() => scrollToSection("petitions")}>Petitions</li>
                <li onClick={() => scrollToSection("drafts")}>Draft Reviews</li>
            </ul>
        </div>
    );
}

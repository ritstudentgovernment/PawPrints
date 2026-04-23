"use client";

import { useEffect, useState } from "react";
import { API_URL } from "../api/specialRoute";

import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import Loading from "../components/loading";
import { sleep } from "../components/loadBuffer";

/* Types */
type Role = {
  id: number | null;
  name: string;
  description?: string | null;
  permissions?: unknown;
};

type User = {
  username: string;
  first_name: string;
  last_name: string;
  roles?: Role[];
};

type ReturnUsers = {
  page_info?: {
    page: number;
    items: number;
    total_items: number;
    total_pages: number;
  };
  users: User[];
};

type ReturnRolesResponse = {
  roles: Role[];
};

export default function AdminUsersSection() {
  // UI state
  const [isLoadingUsers, setIsLoadingUsers] = useState(false);
  const [isLoadingRoles, setIsLoadingRoles] = useState(false);

  // Data state
  const [users, setUsers] = useState<User[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);

  const [searchTerm, setSearchTerm] = useState("");
  const [roleFilter, setRoleFilter] = useState<string>("all");

  const [pendingRoleByUser, setPendingRoleByUser] = useState<Record<string, string>>({});

  // PAGE INFO — ALWAYS SAFE
  const [pageInfo, setPageInfo] = useState({
    page: 1,
    items: 10,
    total_items: 0,
    total_pages: 1,
  });

  const safePageInfo = pageInfo ?? {
    page: 1,
    items: 10,
    total_items: 0,
    total_pages: 1,
  };

  /* ------------------------------- LOAD ROLES ------------------------------ */
  useEffect(() => {
    const loadRoles = async () => {
      try {
        setIsLoadingRoles(true);
        const res = await fetch(`${API_URL}/api/v1/roles/`, {
          credentials: "include",
        });
        const data: ReturnRolesResponse = await res.json();
        setRoles(data.roles || []);
      } catch (err) {
        console.error("Failed to load roles", err);
      } finally {
        setIsLoadingRoles(false);
      }
    };

    loadRoles();
  }, []);

  /* ------------------------------- LOAD USERS ------------------------------ */
  const loadUsers = async (roleName?: string, page = 1, searchTerm?: string) => {
    try {
      setIsLoadingUsers(true);

      const params = new URLSearchParams();
      params.set("page", String(page));
      params.set("items_per_page", "20");

      if (roleName && roleName !== "all") {
        params.set("role_name", roleName);
      }

      if (searchTerm && searchTerm.trim()) {
        params.set("search", searchTerm.trim());
      }

      const res = await fetch(`${API_URL}/api/v1/users/?${params.toString()}`, {
        credentials: "include",
      });

      const data: ReturnUsers = await res.json();

      setUsers(data.users || []);

      // Guarantee SAFE fallback if backend omits page_info
      const info = data.page_info ?? {
        page,
        items: 10,
        total_items: data.users?.length ?? 0,
        total_pages: 1,
      };

      setPageInfo(info);
      sleep(500); // Simulate loading time
    } catch (err) {
      console.error("Failed to load users", err);
    } finally {
      setIsLoadingUsers(false);
    }
  };

  useEffect(() => {
    const debounceTimer = setTimeout(() => {
      loadUsers(roleFilter === "all" ? undefined : roleFilter, 1, searchTerm);
    }, 300); // 300ms debounce

    return () => clearTimeout(debounceTimer);
  }, [searchTerm, roleFilter]);

  /* ------------------------------ FRONTEND SEARCH REMOVED ------------------------------ */
  // Using API search instead of frontend filtering
  const filteredUsers = users;

  /* ------------------------------ EDIT ROLE ------------------------------ */
  const handleRoleSelectChange = (username: string, value: string) => {
    setPendingRoleByUser((prev) => ({ ...prev, [username]: value }));
  };

  const handleSaveRole = async (user: User) => {
    const pendingRoleId = pendingRoleByUser[user.username];
    if (!pendingRoleId) return;

    try {
      const res = await fetch(
        `${API_URL}/api/v1/users/${encodeURIComponent(user.username)}/role`,
        {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({ role_id: Number(pendingRoleId) }),
        }
      );

      if (!res.ok) throw new Error("Failed to update role");

      // Optimistic update
      const selectedRole = roles.find((r) => String(r.id) === pendingRoleId);
      if (selectedRole) {
        setUsers((prev) =>
          prev.map((u) =>
            u.username === user.username ? { ...u, roles: [selectedRole] } : u
          )
        );
      }

      setPendingRoleByUser((prev) => {
        const c = { ...prev };
        delete c[user.username];
        return c;
      });
    } catch (err) {
      console.error("Role update failed", err);
    }
  };

  /* ------------------------------ RENDER ------------------------------ */
  return (
    <div className="admin-section-inner">
      <div className="admin-section-header">
        <h2 className="admin-section-title">Users</h2>
        <p className="admin-section-description">
          View all users, filter by role, and update their role assignments.
        </p>
      </div>

      {/* FILTERS */}
      <div className="admin-filters-row">
        <div className="admin-filter">
          <label className="admin-filter-label">Search users</label>
          <Input
            placeholder="Search by username"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div className="admin-filter">
          <label className="admin-filter-label">Filter by role</label>
          <Select
            value={roleFilter}
            onValueChange={(val) => setRoleFilter(val)}
            disabled={isLoadingRoles}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select role" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All roles</SelectItem>
              {roles.map((r) => (
                <SelectItem key={r.id ?? r.name} value={r.name}>
                  {r.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* PAGINATION */}
      <div className="admin-pagination">
        <Button
          variant="outline"
          disabled={safePageInfo.page <= 1}
          onClick={() =>
            loadUsers(
              roleFilter === "all" ? undefined : roleFilter,
              safePageInfo.page - 1,
              searchTerm
            )
          }
        >
          Previous
        </Button>

        <span className="admin-page-info">
          Page {safePageInfo.page} of {safePageInfo.total_pages}
        </span>

        <Button
          variant="outline"
          disabled={safePageInfo.page >= safePageInfo.total_pages}
          onClick={() =>
            loadUsers(
              roleFilter === "all" ? undefined : roleFilter,
              safePageInfo.page + 1,
              searchTerm
            )
          }
        >
          Next
        </Button>
      </div>

      {/* TABLE */}
      <div className="admin-table-wrapper">
        {isLoadingUsers ? (
          <Loading />
        ) : filteredUsers.length === 0 ? (
          <div className="admin-empty-state">No users found.</div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Username</TableHead>
                <TableHead>First</TableHead>
                <TableHead>Last</TableHead>
                <TableHead>Current role</TableHead>
                <TableHead>New role</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>

            <TableBody>
              {filteredUsers.map((user) => {
                const currentRole = user.roles?.[0]?.name || "";
                const pendingRoleId = pendingRoleByUser[user.username];

                return (
                  <TableRow key={user.username}>
                    <TableCell>{user.username}</TableCell>
                    <TableCell>{user.first_name}</TableCell>
                    <TableCell>{user.last_name}</TableCell>
                    <TableCell>
                      {currentRole ? (
                        <Badge variant="outline">{currentRole}</Badge>
                      ) : (
                        <span className="admin-muted">None</span>
                      )}
                    </TableCell>

                    <TableCell>
                      <Select
                        value={pendingRoleId ?? ""}
                        onValueChange={(v) =>
                          handleRoleSelectChange(user.username, v)
                        }
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select role" />
                        </SelectTrigger>
                        <SelectContent>
                          {roles.map((role) => (
                            <SelectItem
                              key={role.id ?? role.name}
                              value={String(role.id)}
                            >
                              {role.name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </TableCell>

                    <TableCell>
                      <Button size="sm" onClick={() => handleSaveRole(user)}>
                        Save
                      </Button>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        )}
      </div>
    </div>
  );
}

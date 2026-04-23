"use client";

import { useEffect, useState } from "react";
import { API_URL } from "../api/specialRoute";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { Permission } from "@/types/Permission";

type PermissionsResponse = {
  permissions: Permission[];
};

export default function AdminPermissionsSection() {
  const [permissions, setPermissions] = useState<Permission[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    loadPermissions();
  }, []);

  const loadPermissions = async () => {
    try {
      setIsLoading(true);
      const res = await fetch(`${API_URL}/api/v1/permissions/`, {
        credentials: "include",
      });
      const data: PermissionsResponse = await res.json();
      const allPermissions = data.permissions || [];
      
      const permissionsWithNullIds = allPermissions.filter(p => p.id == null);
      if (permissionsWithNullIds.length > 0) {
        console.warn(`Found ${permissionsWithNullIds.length} permission(s) with null IDs:`, permissionsWithNullIds);
      }
      
      const validPermissions = allPermissions.filter(p => p.id != null);
      const sortedPermissions = validPermissions.sort((a, b) => a.id! - b.id!);
      setPermissions(sortedPermissions);
    } catch (err) {
      console.error("Failed to load permissions", err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="admin-section-inner">
      <div className="admin-section-header">
        <h2 className="admin-section-title">Permissions</h2>
        <p className="admin-section-description">
          View all available permissions in the system. These can be assigned to roles.
        </p>
      </div>

      <div className="admin-table-wrapper">
        {isLoading ? (
          <div className="admin-loading">Loading permissions...</div>
        ) : permissions.length === 0 ? (
          <div className="admin-empty-state">No permissions found.</div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ID</TableHead>
                <TableHead>Permission Name</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {permissions.map((perm) => (
                <TableRow key={perm.id}>
                  <TableCell>{perm.id}</TableCell>
                  <TableCell className="font-medium">{perm.name}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </div>
    </div>
  );
}

"use client";

import { useEffect, useState } from "react";
import { API_URL } from "../api/specialRoute";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Checkbox } from "@/components/ui/checkbox";
import { useToast } from "@/hooks/use-toast";
import type { Role } from "@/types/Role";
import type { Permission } from "@/types/Permission";
import type { UserProfile } from "@/types/UserProfile";

type RolesResponse = {
  roles: Role[];
};

type PermissionsResponse = {
  permissions: Permission[];
};

type UsersResponse = {
  page_info?: {
    page: number;
    items: number;
    total_items: number;
    total_pages: number;
  };
  users: UserProfile[];
};

export default function AdminRolesSection() {
  const { toast } = useToast();
  const [roles, setRoles] = useState<Role[]>([]);
  const [permissions, setPermissions] = useState<Permission[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isPermissionsDialogOpen, setIsPermissionsDialogOpen] = useState(false);
  const [isMembersDialogOpen, setIsMembersDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [isDuplicateDialogOpen, setIsDuplicateDialogOpen] = useState(false);

  const [selectedRole, setSelectedRole] = useState<Role | null>(null);
  const [roleToDelete, setRoleToDelete] = useState<Role | null>(null);
  const [roleToDuplicate, setRoleToDuplicate] = useState<Role | null>(null);
  const [formName, setFormName] = useState("");
  const [formDescription, setFormDescription] = useState("");
  const [duplicateRoleName, setDuplicateRoleName] = useState("");
  const [selectedPermissionIds, setSelectedPermissionIds] = useState<number[]>([]);

  // Role members state
  const [roleMembers, setRoleMembers] = useState<UserProfile[]>([]);
  const [isLoadingMembers, setIsLoadingMembers] = useState(false);
  const [membersPage, setMembersPage] = useState(1);
  const [membersPageInfo, setMembersPageInfo] = useState({
    page: 1,
    items: 20,
    total_items: 0,
    total_pages: 1,
  });

  useEffect(() => {
    loadRoles();
    loadPermissions();
  }, []);

  const loadRoles = async () => {
    try {
      setIsLoading(true);
      const res = await fetch(`${API_URL}/api/v1/roles/permissions`, {
        credentials: "include",
      });
      const data: RolesResponse = await res.json();
      setRoles(data.roles || []);
    } catch (err) {
      console.error("Failed to load roles", err);
    } finally {
      setIsLoading(false);
    }
  };

  const loadPermissions = async () => {
    try {
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
      setPermissions(validPermissions);
    } catch (err) {
      console.error("Failed to load permissions", err);
      toast({
        title: "Error",
        description: "Failed to load permissions. Please try again.",
        variant: "destructive",
      });
    }
  };

  const handleCreateRole = async () => {
    if (!formName.trim()) {
      toast({
        title: "Validation Error",
        description: "Role name is required.",
        variant: "destructive",
      });
      return;
    }

    try {
      const permissionsPayload = selectedPermissionIds.map((id) => {
        const perm = permissions.find((p) => p.id === id);
        return { id, name: perm?.name || "" };
      });

      const res = await fetch(`${API_URL}/api/v1/roles/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          name: formName,
          description: formDescription,
          permissions: permissionsPayload,
        }),
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || "Failed to create role");
      }

      await loadRoles();
      setIsCreateDialogOpen(false);
      resetForm();
      toast({
        title: "Success",
        description: `Role "${formName}" created successfully.`,
      });
    } catch (err) {
      console.error("Create role failed", err);
      toast({
        title: "Error",
        description: err instanceof Error ? err.message : "Failed to create role. Please try again.",
        variant: "destructive",
      });
    }
  };

  const handleUpdateRole = async () => {
    if (!selectedRole || !formName.trim()) {
      toast({
        title: "Validation Error",
        description: "Role name is required.",
        variant: "destructive",
      });
      return;
    }

    if (selectedRole.id == null) {
      toast({
        title: "Error",
        description: "Cannot update role with invalid ID.",
        variant: "destructive",
      });
      return;
    }

    try {
      const res = await fetch(`${API_URL}/api/v1/roles/${selectedRole.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          name: formName,
          description: formDescription,
        }),
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || "Failed to update role");
      }

      await loadRoles();
      setIsEditDialogOpen(false);
      resetForm();
      toast({
        title: "Success",
        description: `Role "${formName}" updated successfully.`,
      });
    } catch (err) {
      console.error("Update role failed", err);
      toast({
        title: "Error",
        description: err instanceof Error ? err.message : "Failed to update role. Please try again.",
        variant: "destructive",
      });
    }
  };

  const handleUpdatePermissions = async () => {
    if (!selectedRole) return;

    try {
      const res = await fetch(
        `${API_URL}/api/v1/roles/${selectedRole.id}/permissions`,
        {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({
            permission_ids: selectedPermissionIds,
          }),
        }
      );

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || "Failed to update permissions");
      }

      await loadRoles();
      setIsPermissionsDialogOpen(false);
      resetForm();
      toast({
        title: "Success",
        description: `Permissions for "${selectedRole.name}" updated successfully.`,
      });
    } catch (err) {
      console.error("Update permissions failed", err);
      toast({
        title: "Error",
        description: err instanceof Error ? err.message : "Failed to update permissions. Please try again.",
        variant: "destructive",
      });
    }
  };

  const openDeleteDialog = (role: Role) => {
    setRoleToDelete(role);
    setIsDeleteDialogOpen(true);
  };

  const handleDeleteRole = async () => {
    if (!roleToDelete?.id) return;

    try {
      const res = await fetch(`${API_URL}/api/v1/roles/${roleToDelete.id}`, {
        method: "DELETE",
        credentials: "include",
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || "Failed to delete role");
      }

      await loadRoles();
      setIsDeleteDialogOpen(false);
      const deletedRoleName = roleToDelete.name;
      setRoleToDelete(null);
      toast({
        title: "Success",
        description: `Role "${deletedRoleName}" deleted successfully.`,
      });
    } catch (err) {
      console.error("Delete role failed", err);
      toast({
        title: "Error",
        description: err instanceof Error ? err.message : "Failed to delete role. Please try again.",
        variant: "destructive",
      });
    }
  };

  const openDuplicateDialog = (role: Role) => {
    setRoleToDuplicate(role);
    setDuplicateRoleName(`${role.name}_copy`);
    setIsDuplicateDialogOpen(true);
  };

  const handleDuplicateRole = async () => {
    if (!roleToDuplicate?.id || !duplicateRoleName.trim()) {
      toast({
        title: "Validation Error",
        description: "New role name is required.",
        variant: "destructive",
      });
      return;
    }

    try {
      const res = await fetch(
        `${API_URL}/api/v1/roles/${roleToDuplicate.id}/duplicate`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({ new_name: duplicateRoleName }),
        }
      );

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || "Failed to duplicate role");
      }

      await loadRoles();
      setIsDuplicateDialogOpen(false);
      setRoleToDuplicate(null);
      setDuplicateRoleName("");
      toast({
        title: "Success",
        description: `Role duplicated as "${duplicateRoleName}" successfully.`,
      });
    } catch (err) {
      console.error("Duplicate role failed", err);
      toast({
        title: "Error",
        description: err instanceof Error ? err.message : "Failed to duplicate role. Please try again.",
        variant: "destructive",
      });
    }
  };

  const openEditDialog = (role: Role) => {
    setSelectedRole(role);
    setFormName(role.name);
    setFormDescription(role.description || "");
    setIsEditDialogOpen(true);
  };

  const openPermissionsDialog = (role: Role) => {
    setSelectedRole(role);
    const currentPermissionIds = (role.permissions || [])
      .map((p) => p.id)
      .filter((id): id is number => id !== null);
    setSelectedPermissionIds(currentPermissionIds);
    setIsPermissionsDialogOpen(true);
  };

  const resetForm = () => {
    setFormName("");
    setFormDescription("");
    setSelectedPermissionIds([]);
    setSelectedRole(null);
  };

  const togglePermission = (permId: number) => {
    setSelectedPermissionIds((prev) =>
      prev.includes(permId)
        ? prev.filter((id) => id !== permId)
        : [...prev, permId]
    );
  };

  const loadRoleMembers = async (roleName: string, page = 1) => {
    try {
      setIsLoadingMembers(true);
      const res = await fetch(
        `${API_URL}/api/v1/users/?role_name=${encodeURIComponent(roleName)}&page=${page}&items_per_page=20`,
        {
          credentials: "include",
        }
      );
      
      if (!res.ok) {
        console.error('Failed to load role members:', res.status);
        setRoleMembers([]);
        return;
      }

      const data: UsersResponse = await res.json();
      setRoleMembers(data.users || []);
      
      const info = data.page_info ?? {
        page,
        items: 20,
        total_items: data.users?.length ?? 0,
        total_pages: 1,
      };
      setMembersPageInfo(info);
    } catch (err) {
      console.error("Failed to load role members", err);
      setRoleMembers([]);
    } finally {
      setIsLoadingMembers(false);
    }
  };

  const openMembersDialog = (role: Role) => {
    setSelectedRole(role);
    setMembersPage(1);
    loadRoleMembers(role.name, 1);
    setIsMembersDialogOpen(true);
  };

  const handleMembersPageChange = (newPage: number) => {
    if (!selectedRole) return;
    setMembersPage(newPage);
    loadRoleMembers(selectedRole.name, newPage);
  };

  return (
    <div className="admin-section-inner">
      <div className="admin-section-header">
        <h2 className="admin-section-title">Roles</h2>
        <p className="admin-section-description">
          Create, edit, and delete roles. Manage role permissions.
        </p>
      </div>

      <div className="admin-filters-row">
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button onClick={resetForm}>Create New Role</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create New Role</DialogTitle>
              <DialogDescription>
                Add a new role with optional permissions.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label htmlFor="role-name">Role Name</Label>
                <Input
                  id="role-name"
                  value={formName}
                  onChange={(e) => setFormName(e.target.value)}
                  placeholder="e.g., moderator"
                />
              </div>
              <div>
                <Label htmlFor="role-desc">Description</Label>
                <Textarea
                  id="role-desc"
                  value={formDescription}
                  onChange={(e) => setFormDescription(e.target.value)}
                  placeholder="Role description"
                />
              </div>
              <div>
                <Label>Permissions</Label>
                <div className="max-h-48 overflow-y-auto space-y-2 mt-2">
                  {permissions.map((perm) => {
                    if (perm.id == null) return null;
                    const permId = perm.id;
                    const checkboxId = `permission-create-${permId}`;
                    return (
                      <div key={permId} className="flex items-center space-x-2">
                        <Checkbox
                          id={checkboxId}
                          checked={selectedPermissionIds.includes(permId)}
                          onCheckedChange={() => togglePermission(permId)}
                        />
                        <Label htmlFor={checkboxId} className="text-sm cursor-pointer">
                          {perm.name}
                        </Label>
                      </div>
                    );
                  })}
                </div>
              </div>
              <Button onClick={handleCreateRole}>Create Role</Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <div className="admin-table-wrapper">
        {isLoading ? (
          <div className="admin-loading">Loading roles...</div>
        ) : roles.length === 0 ? (
          <div className="admin-empty-state">No roles found.</div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Description</TableHead>
                <TableHead>Permissions</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {roles.map((role) => (
                <TableRow key={role.id}>
                  <TableCell className="font-medium">{role.name}</TableCell>
                  <TableCell>{role.description || "—"}</TableCell>
                  <TableCell>
                    <div className="flex flex-wrap gap-1">
                      {(role.permissions || [])
                        .filter(perm => perm.id != null)
                        .slice(0, 3)
                        .map((perm) => (
                          <Badge key={perm.id ?? perm.name} variant="outline" className="text-xs">
                            {perm.name}
                          </Badge>
                        ))}
                      {(role.permissions || []).length > 3 && (
                        <Badge variant="outline" className="text-xs">
                          +{(role.permissions || []).length - 3} more
                        </Badge>
                      )}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => openMembersDialog(role)}
                      >
                        View Members
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => openEditDialog(role)}
                      >
                        Edit
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => openPermissionsDialog(role)}
                      >
                        Permissions
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => openDuplicateDialog(role)}
                      >
                        Duplicate
                      </Button>
                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={() => openDeleteDialog(role)}
                      >
                        Delete
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </div>

      {/* Edit Role Dialog */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Role</DialogTitle>
            <DialogDescription>
              Update the role name and description.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="edit-role-name">Role Name</Label>
              <Input
                id="edit-role-name"
                value={formName}
                onChange={(e) => setFormName(e.target.value)}
              />
            </div>
            <div>
              <Label htmlFor="edit-role-desc">Description</Label>
              <Textarea
                id="edit-role-desc"
                value={formDescription}
                onChange={(e) => setFormDescription(e.target.value)}
              />
            </div>
            <Button onClick={handleUpdateRole}>Update Role</Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Manage Permissions Dialog */}
      <Dialog
        open={isPermissionsDialogOpen}
        onOpenChange={setIsPermissionsDialogOpen}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Manage Permissions for {selectedRole?.name}</DialogTitle>
            <DialogDescription>
              Select permissions to assign to this role.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="max-h-96 overflow-y-auto space-y-2">
              {permissions.map((perm) => {
                if (perm.id == null) return null;
                const permId = perm.id;
                const checkboxId = `permission-manage-${permId}`;
                return (
                  <div key={permId} className="flex items-center space-x-2">
                    <Checkbox
                      id={checkboxId}
                      checked={selectedPermissionIds.includes(permId)}
                      onCheckedChange={() => togglePermission(permId)}
                    />
                    <Label htmlFor={checkboxId} className="text-sm cursor-pointer">
                      {perm.name}
                    </Label>
                  </div>
                );
              })}
            </div>
            <Button onClick={handleUpdatePermissions}>Save Permissions</Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* View Members Dialog */}
      <Dialog open={isMembersDialogOpen} onOpenChange={setIsMembersDialogOpen}>
        <DialogContent className="max-w-4xl">
          <DialogHeader>
            <DialogTitle>Members with role: {selectedRole?.name}</DialogTitle>
            <DialogDescription>
              Users who have been assigned this role.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            {isLoadingMembers ? (
              <div className="admin-loading">Loading members...</div>
            ) : roleMembers.length === 0 ? (
              <div className="admin-empty-state">No users found with this role.</div>
            ) : (
              <>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Username</TableHead>
                      <TableHead>First Name</TableHead>
                      <TableHead>Last Name</TableHead>
                      <TableHead>Committees</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {roleMembers.map((member) => (
                      <TableRow key={member.username}>
                        <TableCell className="font-medium">{member.username}</TableCell>
                        <TableCell>{member.first_name}</TableCell>
                        <TableCell>{member.last_name}</TableCell>
                        <TableCell>
                          {member.committees && member.committees.length > 0
                            ? member.committees.map((c) => c.name).join(", ")
                            : "—"}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>

                {/* Pagination Controls */}
                <div className="admin-pagination">
                  <Button
                    variant="outline"
                    disabled={membersPage <= 1}
                    onClick={() => handleMembersPageChange(membersPage - 1)}
                  >
                    Previous
                  </Button>

                  <span className="admin-page-info">
                    Page {membersPageInfo.page} of {membersPageInfo.total_pages} 
                    ({membersPageInfo.total_items} total members)
                  </span>

                  <Button
                    variant="outline"
                    disabled={membersPage >= membersPageInfo.total_pages}
                    onClick={() => handleMembersPageChange(membersPage + 1)}
                  >
                    Next
                  </Button>
                </div>
              </>
            )}
          </div>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Role</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete the role &quot;{roleToDelete?.name}&quot;?
              This action cannot be undone and may affect users who have this role.
            </DialogDescription>
          </DialogHeader>
          <div className="flex gap-2 justify-end">
            <Button
              variant="outline"
              onClick={() => {
                setIsDeleteDialogOpen(false);
                setRoleToDelete(null);
              }}
            >
              Cancel
            </Button>
            <Button variant="destructive" onClick={handleDeleteRole}>
              Delete
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Duplicate Role Dialog */}
      <Dialog open={isDuplicateDialogOpen} onOpenChange={setIsDuplicateDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Duplicate Role</DialogTitle>
            <DialogDescription>
              Create a copy of &quot;{roleToDuplicate?.name}&quot; with all its permissions.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="duplicate-role-name">New Role Name</Label>
              <Input
                id="duplicate-role-name"
                value={duplicateRoleName}
                onChange={(e) => setDuplicateRoleName(e.target.value)}
                placeholder="Enter name for duplicated role"
              />
            </div>
            <div className="text-sm text-muted-foreground">
              The new role will have the same permissions as &quot;{roleToDuplicate?.name}&quot;:
              <div className="mt-2 flex flex-wrap gap-1">
                {(roleToDuplicate?.permissions || [])
                  .filter(perm => perm.id != null)
                  .map((perm) => (
                    <Badge key={perm.id ?? perm.name} variant="outline" className="text-xs">
                      {perm.name}
                    </Badge>
                  ))}
              </div>
            </div>
            <div className="flex gap-2 justify-end">
              <Button
                variant="outline"
                onClick={() => {
                  setIsDuplicateDialogOpen(false);
                  setRoleToDuplicate(null);
                  setDuplicateRoleName("");
                }}
              >
                Cancel
              </Button>
              <Button onClick={handleDuplicateRole}>
                Duplicate Role
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}

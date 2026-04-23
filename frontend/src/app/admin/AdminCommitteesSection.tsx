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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import type { Committee } from "@/types/Committee";
import type { UserProfile } from "@/types/UserProfile";
import type { Role } from "@/types/Role";

export default function AdminCommitteesSection() {
  const [committees, setCommittees] = useState<Committee[]>([]);
  const [users, setUsers] = useState<UserProfile[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);
  const [selectedCommitteeMembers, setSelectedCommitteeMembers] = useState<
    UserProfile[]
  >([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingMembers, setIsLoadingMembers] = useState(false);

  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isMembersDialogOpen, setIsMembersDialogOpen] = useState(false);
  const [isAddMemberDialogOpen, setIsAddMemberDialogOpen] = useState(false);
  const [isAddRoleDialogOpen, setIsAddRoleDialogOpen] = useState(false);
  const [isAddRoleToAllDialogOpen, setIsAddRoleToAllDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);

  const [selectedCommittee, setSelectedCommittee] = useState<Committee | null>(null);
  const [committeeToDelete, setCommitteeToDelete] = useState<Committee | null>(null);
  const [formName, setFormName] = useState("");
  const [formDescription, setFormDescription] = useState("");
  const [selectedUsername, setSelectedUsername] = useState("");
  const [selectedRoleId, setSelectedRoleId] = useState<string>("");
  const [userSearchOpen, setUserSearchOpen] = useState(false);
  const [userSearchValue, setUserSearchValue] = useState("");

  useEffect(() => {
    loadCommittees();
    loadUsers();
    loadRoles();
  }, []);

  const loadCommittees = async () => {
    try {
      setIsLoading(true);
      const res = await fetch(`${API_URL}/api/v1/committees/`, {
        credentials: "include",
      });
      const data: Committee[] = await res.json();
      setCommittees(data || []);
    } catch (err) {
      console.error("Failed to load committees", err);
    } finally {
      setIsLoading(false);
    }
  };

  const loadUsers = async () => {
    const itemsPerPage = 100;
    const page = 1;
    
    try {
      const res = await fetch(
        `${API_URL}/api/v1/users/?page=${page}&items_per_page=${itemsPerPage}`,
        {
          credentials: "include",
        }
      );
      
      if (!res.ok) {
        console.error("Failed to load users:", res.status);
        setUsers([]);
        return;
      }
      
      const data = await res.json();
      const pageUsers: UserProfile[] = data.users || [];
      setUsers(pageUsers);
    } catch (err) {
      console.error("Failed to load users", err);
      setUsers([]);
    }
  };

  const searchUsers = async (searchTerm: string) => {
    if (!searchTerm.trim()) {
      await loadUsers();
      return;
    }

    try {
      const res = await fetch(
        `${API_URL}/api/v1/users/?page=1&items_per_page=50&search=${encodeURIComponent(searchTerm.trim())}`,
        {
          credentials: "include",
        }
      );
      
      if (!res.ok) {
        console.error("Failed to search users:", res.status);
        setUsers([]);
        return;
      }
      
      const data = await res.json();
      const searchResults: UserProfile[] = data.users || [];
      setUsers(searchResults);
    } catch (err) {
      console.error("Failed to search users", err);
      setUsers([]);
    }
  };

  const loadRoles = async () => {
    try {
      const res = await fetch(`${API_URL}/api/v1/roles/`, {
        credentials: "include",
      });
      
      if (!res.ok) {
        console.error("Failed to load roles:", res.status);
        setRoles([]);
        return;
      }
      
      const data = await res.json();
      setRoles(data.roles || []);
    } catch (err) {
      console.error("Failed to load roles", err);
      setRoles([]);
    }
  };

  const loadCommitteeMembers = async (committeeId: number) => {
    try {
      setIsLoadingMembers(true);
      const res = await fetch(
        `${API_URL}/api/v1/committees/${committeeId}/members`,
        {
          credentials: "include",
        }
      );
      if (!res.ok) {
        console.error('Failed to load members:', res.status);
        setSelectedCommitteeMembers([]);
        return;
      }
      const data = await res.json();
      setSelectedCommitteeMembers(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Failed to load committee members", err);
      setSelectedCommitteeMembers([]);
    } finally {
      setIsLoadingMembers(false);
    }
  };

  const handleCreateCommittee = async () => {
    if (!formName.trim()) return;

    try {
      const res = await fetch(`${API_URL}/api/v1/committees/create`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          name: formName,
          description: formDescription,
        }),
      });

      if (!res.ok) throw new Error("Failed to create committee");

      await loadCommittees();
      setIsCreateDialogOpen(false);
      resetForm();
    } catch (err) {
      console.error("Create committee failed", err);
    }
  };

  const openDeleteDialog = (committee: Committee) => {
    setCommitteeToDelete(committee);
    setIsDeleteDialogOpen(true);
  };

  const handleDeleteCommittee = async () => {
    if (!committeeToDelete?.id) return;

    try {
      const res = await fetch(
        `${API_URL}/api/v1/committees/delete?committee_id=${committeeToDelete.id}`,
        {
          method: "DELETE",
          credentials: "include",
        }
      );

      if (!res.ok) throw new Error("Failed to delete committee");

      await loadCommittees();
      setIsDeleteDialogOpen(false);
      setCommitteeToDelete(null);
    } catch (err) {
      console.error("Delete committee failed", err);
    }
  };

  const handleAddMember = async () => {
    if (!selectedCommittee || !selectedUsername) return;

    try {
      const res = await fetch(
        `${API_URL}/api/v1/committees/${selectedCommittee.id}/members`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({
            username: selectedUsername,
          }),
        }
      );

      if (!res.ok) throw new Error("Failed to add member");

      await loadCommitteeMembers(selectedCommittee.id!);
      setIsAddMemberDialogOpen(false);
      setSelectedUsername("");
    } catch (err) {
      console.error("Add member failed", err);
    }
  };

  const handleAddRoleToCommittee = async () => {
    if (!selectedCommittee || !selectedRoleId) return;

    try {
      const res = await fetch(
        `${API_URL}/api/v1/committees/${selectedCommittee.id}/members/role/${selectedRoleId}`,
        {
          method: "POST",
          credentials: "include",
        }
      );

      if (!res.ok) throw new Error("Failed to add role members");

      const result = await res.json();
      alert(`Added ${result.added_count} members, skipped ${result.skipped_count} (already members)`);
      
      await loadCommitteeMembers(selectedCommittee.id!);
      setIsAddRoleDialogOpen(false);
      setSelectedRoleId("");
    } catch (err) {
      console.error("Add role to committee failed", err);
      alert("Failed to add role members to committee");
    }
  };

  const handleAddRoleToAllCommittees = async () => {
    if (!selectedRoleId) return;

    try {
      const res = await fetch(
        `${API_URL}/api/v1/committees/members/role/${selectedRoleId}/all`,
        {
          method: "POST",
          credentials: "include",
        }
      );

      if (!res.ok) throw new Error("Failed to add role members to all committees");

      const result = await res.json();
      alert(
        `Added ${result.total_added} members total across ${result.committees.length} committees, ` +
        `skipped ${result.total_skipped} (already members)`
      );
      
      setIsAddRoleToAllDialogOpen(false);
      setSelectedRoleId("");
      await loadCommittees();
    } catch (err) {
      console.error("Add role to all committees failed", err);
      alert("Failed to add role members to all committees");
    }
  };

  const openMembersDialog = (committee: Committee) => {
    if (committee.id == null) {
      console.error("Cannot open members dialog for committee with null ID:", committee);
      return;
    }
    setSelectedCommittee(committee);
    loadCommitteeMembers(committee.id);
    setIsMembersDialogOpen(true);
  };

  const openAddMemberDialog = () => {
    setSelectedUsername("");
    setUserSearchValue("");
    setIsAddMemberDialogOpen(true);
  };

  const openAddRoleDialog = () => {
    setSelectedRoleId("");
    setIsAddRoleDialogOpen(true);
  };

  const openAddRoleToAllDialog = () => {
    setSelectedRoleId("");
    setIsAddRoleToAllDialogOpen(true);
  };

  const resetForm = () => {
    setFormName("");
    setFormDescription("");
    setSelectedCommittee(null);
  };

  // Debounced user search
  useEffect(() => {
    const debounceTimer = setTimeout(() => {
      searchUsers(userSearchValue);
    }, 300);

    return () => clearTimeout(debounceTimer);
  }, [userSearchValue]);

  const filteredUsers = users;

  return (
    <div className="admin-section-inner">
      <div className="admin-section-header">
        <h2 className="admin-section-title">Committees</h2>
        <p className="admin-section-description">
          Manage committees and their members.
        </p>
      </div>

      <div className="admin-filters-row">
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button onClick={resetForm}>Create New Committee</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create New Committee</DialogTitle>
              <DialogDescription>
                Add a new committee to the system.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label htmlFor="committee-name">Committee Name</Label>
                <Input
                  id="committee-name"
                  value={formName}
                  onChange={(e) => setFormName(e.target.value)}
                  placeholder="e.g., Academic Affairs"
                />
              </div>
              <div>
                <Label htmlFor="committee-desc">Description</Label>
                <Textarea
                  id="committee-desc"
                  value={formDescription}
                  onChange={(e) => setFormDescription(e.target.value)}
                  placeholder="Committee description"
                />
              </div>
              <Button onClick={handleCreateCommittee}>Create Committee</Button>
            </div>
          </DialogContent>
        </Dialog>
        
        <Dialog open={isAddRoleToAllDialogOpen} onOpenChange={setIsAddRoleToAllDialogOpen}>
          <DialogTrigger asChild>
            <Button variant="outline" onClick={openAddRoleToAllDialog}>
              Add Role to All Committees
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add Role to All Committees</DialogTitle>
              <DialogDescription>
                Select a role to add all its members to every committee.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label htmlFor="select-role-all">Select Role</Label>
                <Select value={selectedRoleId} onValueChange={setSelectedRoleId}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select a role..." />
                  </SelectTrigger>
                  <SelectContent>
                    {roles.map((role) => (
                      <SelectItem key={role.id} value={role.id?.toString() || ""}>
                        {role.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <Button onClick={handleAddRoleToAllCommittees} disabled={!selectedRoleId}>
                Add Role to All Committees
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <div className="admin-table-wrapper">
        {isLoading ? (
          <div className="admin-loading">Loading committees...</div>
        ) : committees.length === 0 ? (
          <div className="admin-empty-state">No committees found.</div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Description</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {committees.map((committee) => (
                <TableRow key={committee.id}>
                  <TableCell className="font-medium">{committee.name}</TableCell>
                  <TableCell>{committee.description || "—"}</TableCell>
                  <TableCell>
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => openMembersDialog(committee)}
                      >
                        View Members
                      </Button>
                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={() => openDeleteDialog(committee)}
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

      {/* View Members Dialog */}
      <Dialog open={isMembersDialogOpen} onOpenChange={setIsMembersDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Members of {selectedCommittee?.name}</DialogTitle>
            <DialogDescription>
              View and manage committee members.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="flex gap-2">
              <Button onClick={openAddMemberDialog}>Add Member</Button>
              <Button variant="outline" onClick={openAddRoleDialog}>Add Role</Button>
            </div>
            {isLoadingMembers ? (
              <div className="admin-loading">Loading members...</div>
            ) : selectedCommitteeMembers.length === 0 ? (
              <div className="admin-empty-state">No members found.</div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Username</TableHead>
                    <TableHead>Name</TableHead>
                    <TableHead>Roles</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {selectedCommitteeMembers.map((member) => (
                    <TableRow key={member.username}>
                      <TableCell>{member.username}</TableCell>
                      <TableCell>
                        {member.first_name} {member.last_name}
                      </TableCell>
                      <TableCell>
                        {member.roles?.map((r) => r.name).join(", ") || "—"}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </div>
        </DialogContent>
      </Dialog>

      {/* Add Member Dialog */}
      <Dialog
        open={isAddMemberDialogOpen}
        onOpenChange={setIsAddMemberDialogOpen}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add Member to {selectedCommittee?.name}</DialogTitle>
            <DialogDescription>Search and select a user to add to the committee.</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="select-user">Select User</Label>
              <Popover open={userSearchOpen} onOpenChange={setUserSearchOpen}>
                <PopoverTrigger asChild>
                  <Button
                    variant="outline"
                    role="combobox"
                    aria-expanded={userSearchOpen}
                    className="w-full justify-between"
                  >
                    {selectedUsername
                      ? users.find((user) => user.username === selectedUsername)
                          ? `${users.find((user) => user.username === selectedUsername)?.username} (${users.find((user) => user.username === selectedUsername)?.first_name} ${users.find((user) => user.username === selectedUsername)?.last_name})`
                          : "Select user..."
                      : "Select user..."}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-full p-0">
                  <Command>
                    <CommandInput
                      placeholder="Search users..."
                      value={userSearchValue}
                      onValueChange={setUserSearchValue}
                    />
                    <CommandList>
                      <CommandEmpty>No users found.</CommandEmpty>
                      <CommandGroup>
                        {filteredUsers.map((user) => (
                          <CommandItem
                            key={user.username}
                            value={user.username}
                            onSelect={(value) => {
                              setSelectedUsername(value);
                              setUserSearchOpen(false);
                            }}
                          >
                            {user.username} ({user.first_name} {user.last_name})
                          </CommandItem>
                        ))}
                      </CommandGroup>
                    </CommandList>
                  </Command>
                </PopoverContent>
              </Popover>
            </div>
            <Button onClick={handleAddMember} disabled={!selectedUsername}>
              Add Member
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Add Role to Committee Dialog */}
      <Dialog
        open={isAddRoleDialogOpen}
        onOpenChange={setIsAddRoleDialogOpen}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add Role to {selectedCommittee?.name}</DialogTitle>
            <DialogDescription>
              Select a role to add all its members to this committee.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="select-role">Select Role</Label>
              <Select value={selectedRoleId} onValueChange={setSelectedRoleId}>
                <SelectTrigger>
                  <SelectValue placeholder="Select a role..." />
                </SelectTrigger>
                <SelectContent>
                  {roles.map((role) => (
                    <SelectItem key={role.id} value={role.id?.toString() || ""}>
                      {role.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <Button onClick={handleAddRoleToCommittee} disabled={!selectedRoleId}>
              Add Role Members
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Committee</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete the committee &quot;{committeeToDelete?.name}&quot;?
              This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <div className="flex gap-2 justify-end">
            <Button
              variant="outline"
              onClick={() => {
                setIsDeleteDialogOpen(false);
                setCommitteeToDelete(null);
              }}
            >
              Cancel
            </Button>
            <Button variant="destructive" onClick={handleDeleteCommittee}>
              Delete
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}

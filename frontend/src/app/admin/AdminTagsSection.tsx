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
  DialogFooter,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { HexColorPicker } from "react-colorful";

interface Tag {
  id: number;
  name: string;
  description: string | null;
  color: string | null;
  created_at: string;
}

const DEFAULT_COLOR = "#3B82F6";

export default function AdminTagsSection() {
  const [tags, setTags] = useState<Tag[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);

  const [selectedTag, setSelectedTag] = useState<Tag | null>(null);
  const [tagToDelete, setTagToDelete] = useState<Tag | null>(null);

  const [formName, setFormName] = useState("");
  const [formDescription, setFormDescription] = useState("");
  const [formColor, setFormColor] = useState(DEFAULT_COLOR);

  useEffect(() => {
    loadTags();
  }, []);

  const loadTags = async () => {
    setIsLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/v1/tags`, { credentials: "include" });
      if (!res.ok) throw new Error("Failed to fetch tags");
      const data = await res.json();
      setTags(data.tags ?? []);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  const resetForm = () => {
    setFormName("");
    setFormDescription("");
    setFormColor(DEFAULT_COLOR);
  };

  const handleCreateTag = async () => {
    if (!formName.trim()) {
      alert("Tag name is required");
      return;
    }
    try {
      const res = await fetch(`${API_URL}/api/v1/tags`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          name: formName.trim(),
          description: formDescription.trim() || null,
          color: formColor,
        }),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail?.message ?? "Failed to create tag");
      }
      setIsCreateDialogOpen(false);
      resetForm();
      loadTags();
    } catch (e: any) {
      alert(e.message ?? "Failed to create tag");
    }
  };

  const handleEditTag = async () => {
    if (!selectedTag) return;
    if (!formName.trim()) {
      alert("Tag name is required");
      return;
    }
    try {
      const res = await fetch(`${API_URL}/api/v1/tags/${selectedTag.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          name: formName.trim(),
          description: formDescription.trim() || null,
          color: formColor,
        }),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail?.message ?? "Failed to update tag");
      }
      setIsEditDialogOpen(false);
      setSelectedTag(null);
      resetForm();
      loadTags();
    } catch (e: any) {
      alert(e.message ?? "Failed to update tag");
    }
  };

  const handleDeleteTag = async () => {
    if (!tagToDelete) return;
    try {
      const res = await fetch(`${API_URL}/api/v1/tags/${tagToDelete.id}`, {
        method: "DELETE",
        credentials: "include",
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail?.message ?? "Failed to delete tag");
      }
      setIsDeleteDialogOpen(false);
      setTagToDelete(null);
      loadTags();
    } catch (e: any) {
      alert(e.message ?? "Failed to delete tag");
    }
  };

  const openEditDialog = (tag: Tag) => {
    setSelectedTag(tag);
    setFormName(tag.name);
    setFormDescription(tag.description ?? "");
    setFormColor(tag.color ?? DEFAULT_COLOR);
    setIsEditDialogOpen(true);
  };

  const ColorFormFields = () => (
    <>
      <div className="form-field">
        <Label>Color</Label>
        <div style={{ display: "flex", gap: "1rem", alignItems: "center", flexWrap: "wrap" }}>
          <HexColorPicker color={formColor} onChange={setFormColor} />
          <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
            <div
              style={{
                width: 100,
                height: 60,
                backgroundColor: formColor,
                borderRadius: 8,
                border: "2px solid #ddd",
              }}
            />
            <Input
              value={formColor}
              onChange={(e) => setFormColor(e.target.value)}
              placeholder="#RRGGBB"
              maxLength={7}
              style={{ width: 100 }}
            />
          </div>
        </div>
      </div>
    </>
  );

  return (
    <div className="admin-section-content">
      <div className="admin-section-header">
        <h2>Tags Management</h2>
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button onClick={resetForm}>
              <span
                className="material-symbols-outlined"
                style={{ fontSize: "1.2rem", marginRight: "0.5rem" }}
              >
                add
              </span>
              Create Tag
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create New Tag</DialogTitle>
              <DialogDescription>
                Create a new petition tag with a custom colour.
              </DialogDescription>
            </DialogHeader>
            <div className="dialog-form">
              <div className="form-field">
                <Label htmlFor="create-tag-name">Name *</Label>
                <Input
                  id="create-tag-name"
                  value={formName}
                  onChange={(e) => setFormName(e.target.value)}
                  placeholder="e.g., Campus Safety"
                  maxLength={50}
                />
              </div>
              <div className="form-field">
                <Label htmlFor="create-tag-desc">Description</Label>
                <Textarea
                  id="create-tag-desc"
                  value={formDescription}
                  onChange={(e) => setFormDescription(e.target.value)}
                  placeholder="Optional description"
                  maxLength={255}
                  rows={3}
                />
              </div>
              <ColorFormFields />
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={handleCreateTag}>Create Tag</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {isLoading ? (
        <div className="loading-state">Loading tags…</div>
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>ID</TableHead>
              <TableHead>Name</TableHead>
              <TableHead>Description</TableHead>
              <TableHead>Color</TableHead>
              <TableHead>Preview</TableHead>
              <TableHead>Created</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {tags.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} className="text-center">
                  No tags yet. Create your first tag!
                </TableCell>
              </TableRow>
            ) : (
              tags.map((tag) => (
                <TableRow key={tag.id}>
                  <TableCell>{tag.id}</TableCell>
                  <TableCell style={{ fontWeight: 500 }}>{tag.name}</TableCell>
                  <TableCell>{tag.description ?? "—"}</TableCell>
                  <TableCell>
                    <code style={{ fontSize: "0.85rem" }}>{tag.color ?? "—"}</code>
                  </TableCell>
                  <TableCell>
                    {tag.color && (
                      <div
                        style={{
                          width: 40,
                          height: 24,
                          backgroundColor: tag.color,
                          borderRadius: 4,
                          border: "1px solid #ddd",
                        }}
                      />
                    )}
                  </TableCell>
                  <TableCell>
                    {new Date(tag.created_at).toLocaleDateString()}
                  </TableCell>
                  <TableCell>
                    <div style={{ display: "flex", gap: "0.5rem" }}>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => openEditDialog(tag)}
                      >
                        Edit
                      </Button>
                      <Button
                        variant="destructive"
                        size="sm"
                        onClick={() => {
                          setTagToDelete(tag);
                          setIsDeleteDialogOpen(true);
                        }}
                      >
                        Delete
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      )}

      {/* Edit Dialog */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Tag</DialogTitle>
            <DialogDescription>Update tag information and colour.</DialogDescription>
          </DialogHeader>
          <div className="dialog-form">
            <div className="form-field">
              <Label htmlFor="edit-tag-name">Name *</Label>
              <Input
                id="edit-tag-name"
                value={formName}
                onChange={(e) => setFormName(e.target.value)}
                maxLength={50}
              />
            </div>
            <div className="form-field">
              <Label htmlFor="edit-tag-desc">Description</Label>
              <Textarea
                id="edit-tag-desc"
                value={formDescription}
                onChange={(e) => setFormDescription(e.target.value)}
                maxLength={255}
                rows={3}
              />
            </div>
            <ColorFormFields />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsEditDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleEditTag}>Save Changes</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Tag</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete &ldquo;{tagToDelete?.name}&rdquo;? This
              cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsDeleteDialogOpen(false)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={handleDeleteTag}>
              Delete Tag
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

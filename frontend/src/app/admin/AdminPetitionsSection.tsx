"use client";

import { useEffect, useState } from "react";
import { API_URL } from "../api/specialRoute";
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
  DialogFooter,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

interface Petition {
  id: number;
  title: string;
  description: string;
  total_signatures: number;
  created_at: string;
  status: number | string;
  author_display_name: string;
}

interface MarkedPetition {
  id: number;
  petition_id: number;
  petition_title: string;
  marked_at: string;
  marked_by: string | null;
  deletion_scheduled_at: string;
  reason: string | null;
  days_until_deletion: number;
}

function getStatusName(status: number | string): string {
  const s = typeof status === "number" ? status : parseInt(status as string, 10);
  switch (s) {
    case 0: return "Active";
    case 1: return "Charged";
    case 2: return "Responded";
    case 3: return "Expired";
    default: return typeof status === "string" ? status : "Unknown";
  }
}

function getStatusColor(status: number | string): string {
  const s = typeof status === "number" ? status : parseInt(status as string, 10);
  switch (s) {
    case 0: return "#10B981";
    case 1: return "#F59E0B";
    case 2: return "#3B82F6";
    case 3: return "#6B7280";
    default: return "#6B7280";
  }
}

export default function AdminPetitionsSection() {
  const [allPetitions, setAllPetitions] = useState<Petition[]>([]);
  const [markedPetitions, setMarkedPetitions] = useState<MarkedPetition[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingMarked, setIsLoadingMarked] = useState(false);
  const [activeTab, setActiveTab] = useState("all");

  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [isCancelDialogOpen, setIsCancelDialogOpen] = useState(false);
  const [petitionToDelete, setPetitionToDelete] = useState<Petition | null>(null);
  const [markedToCancel, setMarkedToCancel] = useState<MarkedPetition | null>(null);
  const [deleteReason, setDeleteReason] = useState("");

  useEffect(() => {
    loadPetitions();
    loadMarkedPetitions();
  }, []);

  const loadPetitions = async () => {
    setIsLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/v1/petitions?page=1&per_page=100`, {
        credentials: "include",
      });
      if (!res.ok) throw new Error("Failed to fetch petitions");
      const data = await res.json();
      setAllPetitions(data.petitions ?? []);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  const loadMarkedPetitions = async () => {
    setIsLoadingMarked(true);
    try {
      const res = await fetch(
        `${API_URL}/api/v1/admin/petitions/marked-for-deletion`,
        { credentials: "include" }
      );
      if (!res.ok) throw new Error("Failed to fetch marked petitions");
      const data = await res.json();
      setMarkedPetitions(Array.isArray(data) ? data : []);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoadingMarked(false);
    }
  };

  const handleMarkForDeletion = async () => {
    if (!petitionToDelete) return;
    try {
      const res = await fetch(
        `${API_URL}/api/v1/petitions/${petitionToDelete.id}/mark-for-deletion`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({ reason: deleteReason.trim() || null }),
        }
      );
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail?.message ?? "Failed to mark petition for deletion");
      }
      setIsDeleteDialogOpen(false);
      setPetitionToDelete(null);
      setDeleteReason("");
      loadPetitions();
      loadMarkedPetitions();
    } catch (e: any) {
      alert(e.message ?? "Failed to mark petition for deletion");
    }
  };

  const handleCancelDeletion = async () => {
    if (!markedToCancel) return;
    try {
      const res = await fetch(
        `${API_URL}/api/v1/petitions/${markedToCancel.petition_id}/cancel-deletion`,
        { method: "DELETE", credentials: "include" }
      );
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail?.message ?? "Failed to cancel deletion");
      }
      setIsCancelDialogOpen(false);
      setMarkedToCancel(null);
      loadPetitions();
      loadMarkedPetitions();
    } catch (e: any) {
      alert(e.message ?? "Failed to cancel deletion");
    }
  };

  return (
    <div className="admin-section-content">
      <div className="admin-section-header">
        <h2>Petitions Management</h2>
        <p style={{ fontSize: "0.9rem", color: "#666", marginTop: "0.5rem" }}>
          Manage petitions and scheduled deletion
        </p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="all">All Petitions ({allPetitions.length})</TabsTrigger>
          <TabsTrigger value="marked">
            Marked for Deletion ({markedPetitions.length})
          </TabsTrigger>
        </TabsList>

        <TabsContent value="all">
          {isLoading ? (
            <div className="loading-state">Loading petitions…</div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ID</TableHead>
                  <TableHead>Title</TableHead>
                  <TableHead>Author</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Signatures</TableHead>
                  <TableHead>Created</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {allPetitions.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center">
                      No petitions found
                    </TableCell>
                  </TableRow>
                ) : (
                  allPetitions.map((p) => (
                    <TableRow key={p.id}>
                      <TableCell>{p.id}</TableCell>
                      <TableCell>
                        <div style={{ maxWidth: 300 }}>
                          <div style={{ fontWeight: 500 }}>{p.title}</div>
                        </div>
                      </TableCell>
                      <TableCell>{p.author_display_name}</TableCell>
                      <TableCell>
                        <span
                          style={{
                            padding: "0.25rem 0.75rem",
                            borderRadius: "9999px",
                            fontSize: "0.75rem",
                            fontWeight: 500,
                            backgroundColor: getStatusColor(p.status) + "20",
                            color: getStatusColor(p.status),
                          }}
                        >
                          {getStatusName(p.status)}
                        </span>
                      </TableCell>
                      <TableCell>{p.total_signatures}</TableCell>
                      <TableCell>
                        {new Date(p.created_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell>
                        <Button
                          variant="destructive"
                          size="sm"
                          onClick={() => {
                            setPetitionToDelete(p);
                            setDeleteReason("");
                            setIsDeleteDialogOpen(true);
                          }}
                        >
                          <span
                            className="material-symbols-outlined"
                            style={{ fontSize: "1rem", marginRight: "0.25rem" }}
                          >
                            delete
                          </span>
                          Mark for Deletion
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          )}
        </TabsContent>

        <TabsContent value="marked">
          {isLoadingMarked ? (
            <div className="loading-state">Loading marked petitions…</div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Petition ID</TableHead>
                  <TableHead>Title</TableHead>
                  <TableHead>Marked At</TableHead>
                  <TableHead>Marked By</TableHead>
                  <TableHead>Deletion Date</TableHead>
                  <TableHead>Days Left</TableHead>
                  <TableHead>Reason</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {markedPetitions.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={8} className="text-center">
                      No petitions marked for deletion
                    </TableCell>
                  </TableRow>
                ) : (
                  markedPetitions.map((m) => (
                    <TableRow key={m.id}>
                      <TableCell>{m.petition_id}</TableCell>
                      <TableCell>
                        <div style={{ maxWidth: 250, fontWeight: 500 }}>
                          {m.petition_title}
                        </div>
                      </TableCell>
                      <TableCell>
                        {new Date(m.marked_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell>{m.marked_by ?? "—"}</TableCell>
                      <TableCell>
                        {new Date(m.deletion_scheduled_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell>
                        <span
                          style={{
                            padding: "0.25rem 0.75rem",
                            borderRadius: "9999px",
                            fontSize: "0.75rem",
                            fontWeight: 500,
                            backgroundColor:
                              m.days_until_deletion <= 7
                                ? "#FEE2E2"
                                : m.days_until_deletion <= 30
                                ? "#FEF3C7"
                                : "#DBEAFE",
                            color:
                              m.days_until_deletion <= 7
                                ? "#DC2626"
                                : m.days_until_deletion <= 30
                                ? "#D97706"
                                : "#2563EB",
                          }}
                        >
                          {m.days_until_deletion} days
                        </span>
                      </TableCell>
                      <TableCell>
                        <div
                          style={{
                            maxWidth: 200,
                            fontSize: "0.85rem",
                            overflow: "hidden",
                            textOverflow: "ellipsis",
                            whiteSpace: "nowrap",
                          }}
                          title={m.reason ?? ""}
                        >
                          {m.reason ?? "—"}
                        </div>
                      </TableCell>
                      <TableCell>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            setMarkedToCancel(m);
                            setIsCancelDialogOpen(true);
                          }}
                        >
                          Cancel Deletion
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          )}
        </TabsContent>
      </Tabs>

      {/* Mark for Deletion Dialog */}
      <Dialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Mark Petition for Deletion</DialogTitle>
            <DialogDescription>
              &ldquo;{petitionToDelete?.title}&rdquo; will be hidden immediately and
              automatically deleted in 60 days.
            </DialogDescription>
          </DialogHeader>
          <div className="dialog-form">
            <div className="form-field">
              <Label htmlFor="delete-reason">Reason (optional)</Label>
              <Textarea
                id="delete-reason"
                value={deleteReason}
                onChange={(e) => setDeleteReason(e.target.value)}
                placeholder="e.g., Violates terms of service, spam…"
                maxLength={500}
                rows={4}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsDeleteDialogOpen(false)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={handleMarkForDeletion}>
              Mark for Deletion
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Cancel Deletion Dialog */}
      <Dialog open={isCancelDialogOpen} onOpenChange={setIsCancelDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Cancel Deletion</DialogTitle>
            <DialogDescription>
              Cancel scheduled deletion for &ldquo;{markedToCancel?.petition_title}&rdquo;?
              The petition will be restored and visible to the public again.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsCancelDialogOpen(false)}>
              No, Keep Deletion
            </Button>
            <Button onClick={handleCancelDeletion}>Yes, Cancel Deletion</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

'use client';

import { API_URL } from '../../api/specialRoute';
import { useAuth } from '../../hooks/useAuth';
import React, { useState, useEffect, useRef } from 'react';
import { useParams } from 'next/navigation';
import DOMPurify from 'isomorphic-dompurify';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import NavBar from '../../components/NavBar';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"

import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import './page.css';
import { PetitionType } from '@/app/components/Petition';
import LexicalViewer from '@/app/components/Petition/LexicalViewer';
import Loading from '@/app/components/loading';
import Forbidden from '@/app/forbidden';
import { removeAmp } from '@/app/components/removeAmp';
import { ConfirmButton } from '@/app/components/ConfirmButton';

type ReviewType = {
  id: number;
  message: string;
  reviewer_id: string;
  update_id: number;
  is_approved: boolean;
  created_at: string;
};

type UpdateType = {
  id: number;
  message: string;
  created_at: string;
  author_id: string | null;
  approved_by: string | null;
  is_draft: boolean;
  is_approved: boolean;
  submission_thread_id: number;
  reviews: ReviewType[];
};

type ResponseType = {
  is_response: boolean;
  update: UpdateType;
  review: ReviewType[];
}

enum TextAreaMode {
  REVIEW = "review",
  DRAFT = "draft",
  EDIT = "edit",
}

import dynamic from "next/dynamic";
import { isLexicalEmpty } from '../../components/Petition/LexicalEditor';
import { TagType } from '@/app/components/SidebarItem';

const LexicalEditor = dynamic(() => import("../../components/Petition/LexicalEditor"), {
  ssr: false,
  loading: () => <div className="min-h-[200px] border rounded-md bg-gray-50 animate-pulse">Loading editor...</div>
});

export default function ReviewPage() {
  const { id } = useParams();
  const { user } = useAuth();

  const [responses, setResponses] = useState<ResponseType[]>([]);
  const [petition, setPetition] = useState<PetitionType | null>(null);
  const [currentUpdate, setCurrentUpdate] = useState<UpdateType | null>(null);
  const [mostRecentUpdate, setMostRecentUpdate] = useState<UpdateType | null>(null);
  const [isCharged, setIsCharged] = useState<boolean>(false);
  const [committees, setCommittees] = useState<TagType[]>([]);
  const [selectedCommittee, setSelectedCommittee] = useState('');
  const [assignedCommittee, setAssignedCommittee] = useState<TagType | null>(null);
  const { isAdmin, isCommitteeMember } = useAuth();
  const bottom = useRef<HTMLDivElement | null>(null);
  const [textArea, setTextArea] = useState<string>("");
  const [textAreaMode, setTextAreaMode] = useState<TextAreaMode>(TextAreaMode.DRAFT);
  const [description, setDescription] = useState<string>("");

  function scrollToBottom() {
    if (bottom.current) {
      bottom.current.scrollIntoView({ behavior: 'smooth' });
    }
  }

  async function fetchUpdates() {
    const url = `${API_URL}/api/v1/petitions/${id}/admin/timeline`;

    const res = await fetch(url, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
    });

    if (!res.ok) {
      console.error("API error:", res.status);
      return;
    }

    const data = await res.json();

    setResponses(data.petition_updates);
    setMostRecentUpdate(null);
    setDescription(data.petition_description);
  }

  useEffect(() => {
    fetchUpdates();
  }, [id]);

  useEffect(() => {
    async function fetchPetition() {
      const url = `${API_URL}/api/v1/petitions/${id}`;
      const res = await fetch(url, {
        method: "GET",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
      });
      if (!res.ok) {
        return;
      }
      const data = await res.json();

      setPetition(data);
    }

    fetchPetition();
  }, [id]);

  useEffect(() => {
    async function fetchCommittees() {
      const url = `${API_URL}/api/v1/committees/`;
      const res = await fetch(url, {
        method: "GET",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
      });
      if (!res.ok) {
        console.error("API error:", res.status);
        return;
      }
      const data: TagType[] = await res.json();
      setCommittees(data);
    }

    fetchCommittees();
  }, []);


  const handleEditUpdate = (update: UpdateType) => {
    setTextAreaMode(TextAreaMode.EDIT);
    setTextArea(update.message);
    scrollToBottom();
  }

  const handleWriteReview = (update: UpdateType) => {
    setCurrentUpdate(update);
    setTextAreaMode(TextAreaMode.REVIEW);
    setTextArea("");
    scrollToBottom();
  };

  async function assignCommittee(committeeID: number) {
    try {
      const payload = {
        committee_id: committeeID,
      };

      const res = await fetch(`${API_URL}/api/v1/petitions/${id}/charge`, {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const err = await res.text();
        console.error("Backend error:", err);
        alert("Failed to charge petition. Check console for details.");
        return;
      }
      alert("Petition charged successfully.");
      setAssignedCommittee(committees.find(c => c.id === committeeID) || null);
      setIsCharged(true);
    } catch (err) {
      console.error("Submit error:", err);
      alert("Something went wrong.");
    }
  };

  async function unassignCommittee() {
    try {
      const payload = {
        committee_id: assignedCommittee?.id || null,
      };

      const res = await fetch(`${API_URL}/api/v1/petitions/${id}/unassign`, {
        method: "DELETE",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const err = await res.text();
        console.error("Backend error:", err);
        alert("Failed to unassign committee. Check console for details.");
        return;
      }
      alert("Committee unassigned successfully.");
      setAssignedCommittee(null);
      setIsCharged(false);
    } catch (err) {
      console.error("Submit error:", err);
      alert("Something went wrong.");
    }
  };

  async function approveUpdate(updateId: number) {
    try {
      const payload = {
        update_id: updateId,
        message: "Update approved and published.",
        approve: true,
      };

      const res = await fetch(`${API_URL}/api/v1/petitions/${id}/review`, {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const err = await res.text();
        console.error("Backend error:", err);
        alert("Failed to approve response. Check console for details.");
        return;
      }
      alert("Update approved and published successfully.");
      await fetchUpdates();
    } catch (err) {
      console.error("Submit error:", err);
      alert("Something went wrong.");
    }
  }

  const handleMainAction = () => {
    // reviewing
    switch (textAreaMode) {
      case TextAreaMode.EDIT:
        const targetId = mostRecentUpdate?.id || null;
        handleEditDraft(textArea, targetId);
        return;
      case TextAreaMode.DRAFT:
        if (textArea) {
          const targetId = mostRecentUpdate?.id || null;
          handleSaveDraft(textArea, targetId);
        }
    }
  };

  const handleSubmitReview = (isApproved: boolean) => {
    if (!isApproved && isLexicalEmpty(textArea)) {
      alert("Denial must come with a message.");
      return;
    }
    if (currentUpdate?.id) {
      handleSaveReview(currentUpdate.id, isApproved, textArea);
    }
  };

  // dynamic button label based on context
  const getButtonLabel = () => {
    switch (textAreaMode) {
      case TextAreaMode.EDIT:
        return "Save Changes";
      case TextAreaMode.DRAFT:
        return "Submit Update For Review";
      case TextAreaMode.REVIEW:
        return "Submit Review For Update";
    }
  };

  async function handleSaveReview(updateId: number, isApproved: boolean, message: string) {
    try {
      const payload = {
        update_id: updateId,
        message: message,
        approve: isApproved,
      };

      const res = await fetch(`${API_URL}/api/v1/petitions/${id}/review`, {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const err = await res.text();
        console.error("Backend error:", err);
        alert("Failed to submit review. Check console for details.");
        return;
      }

      alert("Review saved successfully.");
      await fetchUpdates();
      setTextArea("");
      setTextAreaMode(TextAreaMode.DRAFT)
      setCurrentUpdate(null);
    } catch (err) {
      console.error("Submit error:", err);
      alert("Something went wrong.");
    }
  }

  async function handleSaveDraft(message: string, draftId?: number | null) {
    try {
      const payload = {
        is_draft: true,
        is_response: false,
        original_draft_id: draftId,
        message: message,
      };

      const res = await fetch(`${API_URL}/api/v1/petitions/${id}/draft_update`, {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const err = await res.text();
        console.error("Backend error:", err);
        alert("Failed to save draft. Check console for details.");
        return;
      }
      alert("Draft saved successfully.");
      await fetchUpdates();
      setTextArea("");
      setTextAreaMode(TextAreaMode.DRAFT)
    } catch (err) {
      console.error("Submit error:", err);
      alert("Something went wrong.");
    }
  }

  async function handleEditDraft(message: string, draftId?: number | null) {
    if (!draftId) {
      console.error("No draftId provided");
      return;
    }

    const existing = responses
      .map(r => r.update)
      .find(update => update.id === draftId);
    if (!existing) {
      console.error("Update not found:", draftId);
      return;
    }
    const updatedObject = {
      ...existing,
      message: message,
    };


    try {
      const res = await fetch(`${API_URL}/api/v1/petitions/${id}/draft_update`, {
        method: "PUT",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(updatedObject),
      });

      if (!res.ok) {
        const err = await res.text();
        console.error("Backend error:", err);
        alert("Failed to update draft. Check console for details.");
        return;
      }

      alert("Draft updated successfully.");
      await fetchUpdates();

    } catch (err) {
      console.error("Submit error:", err);
      alert("Something went wrong.");
    }

    setResponses((prevResponses) =>
      prevResponses.map((item) => {
        if (item.update.id === draftId) {
          console.log("Updating item with id:", draftId);
          return {
            ...item,
            update: {
              ...item.update,
              message: message,
            },
          };
        }

        return item;
      })
    );

    setTextArea("");
    setTextAreaMode(TextAreaMode.DRAFT)
  }


  async function handleDeleteDraft(updateId: number, fromReview?: boolean | false) {
    try {
      const res = await fetch(`${API_URL}/api/v1/petitions/${id}/draft_update/${updateId}`, {
        method: "DELETE",
        credentials: "include",
      });
      if (!res.ok) {
        const err = await res.text();
        console.error("Backend error:", err);
        alert("Failed to delete draft. Check console for details.");
        return;
      }

      if (!fromReview) alert("Draft deleted successfully.");
      await fetchUpdates();
    } catch (err) {
      console.error("Delete error:", err);
      alert("Something went wrong.");
    }
  }

  async function publishResponse(message: string, draftId?: number | null) {
    try {
      const payload = {
        is_draft: false,
        is_response: true,
        original_draft_id: draftId,
        message: message,
      };

      const res = await fetch(`${API_URL}/api/v1/petitions/${id}/draft_update`, {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const err = await res.text();
        console.error("Backend error:", err);
        alert("Failed to publish response. Check console for details.");
        return;
      }

      const newUpdate = await res.json();
      setResponses((prev) => [...prev, newUpdate]);

      alert("Response published successfully.");
      setTextArea("");
      setTextAreaMode(TextAreaMode.DRAFT)
    } catch (err) {
      console.error("Submit error:", err);
      alert("Something went wrong.");
    }
  }

  useEffect(() => {
    setMostRecentUpdate(
      responses.length > 0 ? responses[responses.length - 1].update : null
    );
  }, [responses]);

  if (!petition && !responses.length) {
    return (
      <main className="main">
        <NavBar />
        <Loading />
      </main>
    );
  }

  const clean_desc = petition ? DOMPurify.sanitize(description, {
    USE_PROFILES: { html: true },
  }) : "";


  if (!isAdmin && !isCommitteeMember) {
    return (
      <main className="main">
        <Forbidden />
      </main>
    );
  }


  return (
    <main className="main">
      <NavBar />
      <main className="outerreview flex flex-col lg:flex-row gap-6 lg:gap-8 max-w-[1600px] mx-auto items-start">
        {/* Petition info panel */}
        <div className="petition-panel lg:sticky lg:top-24 lg:w-[400px] xl:w-[500px] flex-shrink-0 lg:max-h-[calc(100vh-8rem)] overflow-y-auto hidden-scrollbar">
          <Card className="petition-card">
            <CardHeader>
              <CardTitle>{removeAmp(petition?.title || "")}</CardTitle>
            </CardHeader>
            <CardContent className="petition-card-data">
              <div className="flex flex-col gap-1 text-sm text-gray-600 border-b pb-4">
                <span className="data-item"> <b>Author: </b>{petition?.author?.username ?? "Unknown"}</span>
                <span className="data-item"> <b>Signatures: </b>{petition?.total_signatures}</span>
                <span className="data-item"> <b>Status: </b>{
                  petition?.status === 0 ? "Active"
                    : petition?.status === 1 ? "Charged"
                      : petition?.status === 2 ? "Responded"
                        : "Expired"
                }</span>
              </div>
              <div className="description">
                <h2>Description:</h2>
                <LexicalViewer content={clean_desc} />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Timeline Panel */}
        <div className="response-panel flex-1 w-full min-w-0 mt-0 lg:mt-0 lg:h-[calc(100vh-8rem)] flex flex-col">
          <div className="messages overflow-y-auto flex-1 min-h-0 pr-2">
            {responses.map((r) => (
              <div key={r.update.id} className="update-block">

                <div className="update-row w-full" key={r.update.id}>

                  <div
                    className={`message flex-1 w-full ${r.update.is_approved || r.is_response ? (r.is_response ? "response-msg" : "approved-msg") : "draft-msg"}`}
                  >
                    <div className="flex justify-between items-start mb-2 border-b pb-2 border-gray-300/30">
                      <h2>{`${r.update.is_approved || r.is_response ? (r.is_response ? "Approved Response" : "Approved Update") : "Draft Message"}`}</h2>
                      <span className="meta text-xs">
                        <b>{r.update.author_id ?? "Unknown"}</b> — {new Date(r.update.created_at).toLocaleString()}
                      </span>
                    </div>
                    <LexicalViewer content={r.update.message} />

                    {!r.is_response && (
                      <div className="review-buttons">

                        {/* Buttons for editing and deleting drafts (only if it's yours) */}
                        {r.update.is_draft && r.update.author_id === user?.username && (
                          <div className="modify">
                            <button
                              type="button"
                              onClick={() => handleEditUpdate(r.update)}
                              className={"modify-item edit"}
                              title={"Edit Update Text"}
                            >
                              <i className="edit-icon icon" />
                            </button>
                            <ConfirmButton
                              title="Delete Update Draft?"
                              description="This will delete this update draft permanently."
                              onConfirm={() => handleDeleteDraft(r.update.id)}
                              className="modify-item delete"
                            >
                              <i className="delete-icon icon" />
                            </ConfirmButton>
                          </div>
                        )}

                        {isAdmin && (
                          <>
                            {r.update.is_draft && (
                              <Button className="review-btn" onClick={() => handleWriteReview(r.update)}>
                                Write a Review
                              </Button>
                            )}
                          </>
                        )}
                      </div>
                    )}
                  </div>
                </div>


                {/* Render Reviews for this update */}
                {r.review && r.review.length > 0 && (
                  <div className="review-container">
                    {r.review.map((review, index) => (
                      <div key={`review-${index}-${review.id}`} className="review-msg">
                        <LexicalViewer content={review.message} />
                        <span className="meta">
                          {review.reviewer_id} —{" "}
                          {new Date(review.created_at).toLocaleString()}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>


          <div className="response-editor">

            {/* Show context of the update being reviewed */}
            {textAreaMode === TextAreaMode.REVIEW && currentUpdate && (
              <div className="review-context">
                <b>Reviewing Update:</b>
                <LexicalViewer content={currentUpdate.message} />
                <Button
                  variant="ghost"
                  className="cancel-review-btn"
                  onClick={() => {
                    setCurrentUpdate(null);
                    setTextAreaMode(TextAreaMode.DRAFT);
                    setTextArea("");
                  }}
                >
                  Cancel Review
                </Button>
              </div>
            )}

            {/* Editing Label */}
            {textAreaMode === TextAreaMode.EDIT && (
              <div className="edit-context">
                <b>Editing Draft</b>
                <Button
                  variant="ghost"
                  className="cancel-edit-btn"
                  onClick={() => {
                    setTextArea("");
                    setTextAreaMode(TextAreaMode.DRAFT);
                  }}
                >
                  Cancel Edit
                </Button>
              </div>
            )}

            {/* Editor */}
            <LexicalEditor
              placeholderText={`Write your ${textAreaMode}...`}
              value={textArea}
              onChange={setTextArea}
            />


            <div className="editor-actions">
              {/* Assigning To Committee Button (Admin Only) */}
              {isAdmin && textAreaMode == TextAreaMode.DRAFT && (
                <Dialog>
                  <form>
                    <DialogTrigger asChild>
                      {isCharged ? (
                        <Button className="assign-btn" variant="outline" onClick={unassignCommittee}>
                          Unassign
                        </Button>) :
                        <Button className="assign-btn" variant="outline" >
                          Assign Committee
                        </Button>
                      }
                    </DialogTrigger>
                    <DialogContent className="sm:max-w-[425px]">
                      <DialogHeader>
                        <DialogTitle>Charge Petition to Committee</DialogTitle>
                        <DialogDescription>
                          Assign a committee to review this petition.
                        </DialogDescription>
                      </DialogHeader>
                      <div className="grid gap-4">
                        <div className="grid gap-3">
                          <Select
                            value={selectedCommittee}
                            onValueChange={setSelectedCommittee}
                          >
                            <SelectTrigger className="w-full max-w-48">
                              {<SelectValue placeholder="Select a committee" />}
                            </SelectTrigger>
                            <SelectContent
                              position="popper"
                              side="bottom"
                              align="start"
                              sideOffset={4}
                              avoidCollisions={false}
                              className="max-h-60 overflow-y-auto"
                              onWheel={(e: React.WheelEvent) => e.stopPropagation()}
                            >
                              <SelectGroup>
                                {committees.map((committee) => (
                                  <SelectItem
                                    key={committee.id}
                                    value={committee.id.toString()}
                                  >
                                    {committee.name}
                                  </SelectItem>
                                ))}
                              </SelectGroup>
                            </SelectContent>
                          </Select>
                        </div>
                      </div>
                      <DialogFooter>
                        <DialogClose asChild>
                          <Button variant="outline">Cancel</Button>
                        </DialogClose>
                        <Button
                          disabled={!selectedCommittee}
                          onClick={() => assignCommittee(Number(selectedCommittee))}
                        >
                          Charge Petition
                        </Button>
                      </DialogFooter>
                    </DialogContent>
                  </form>
                </Dialog>
              )}

              {/* Button to Submit Update */}

              {textAreaMode !== TextAreaMode.REVIEW && (
                <Button
                  className="draft-btn"
                  onClick={handleMainAction}
                  disabled={!textArea}
                >
                  {getButtonLabel()}
                </Button>
              )}

              {textAreaMode === TextAreaMode.REVIEW && (
                <div>
                  <div className="flex items-center gap-3">
                    <ConfirmButton
                      onConfirm={() => handleSubmitReview(true)}
                      title="Approve Update?"
                      description="This will publish the update to the public timeline immediately."
                      className="assign-btn"
                    >
                      Approve as Update
                    </ConfirmButton>

                    <ConfirmButton
                      onConfirm={() => {
                        if (!currentUpdate) {
                          alert("Error publishing response...")
                          return;
                        }
                        handleDeleteDraft(currentUpdate.id, true);
                        publishResponse(currentUpdate.message);
                      }}
                      title="Mark as Official Response?"
                      description="This creates an 'Official Response'. Use this for final statements."
                      variant="outline"
                      className="publish-btn"
                    >
                      Approve as Response
                    </ConfirmButton>

                    <Button variant="ghost" className="text-red-600 hover:text-red-700 hover:bg-red-200" onClick={() => handleSubmitReview(false)}>
                      Deny
                    </Button>

                  </div>
                </div>

              )}

              {/* Button to Submit Official Response Without Drafting for Review (Admin Only) */}
              {isAdmin && textAreaMode === TextAreaMode.DRAFT && (
                <ConfirmButton
                  title="Are you sure?"
                  description="Submitting an 'Official Response' will make this final statement visible to the public. You cannot edit or delete this response after submission."
                  className='publish-btn'
                  onConfirm={() => publishResponse(textArea)}
                >
                  Submit Official Response
                </ConfirmButton>
              )}

            </div>
          </div>
        </div>
      </main>

      {/* for scrolling to bottom */}
      <div style={{ float: "left", clear: "both" }}
        ref={bottom}>
      </div>
    </main>
  );
}

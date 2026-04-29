"use client";

import { useEffect, useState } from "react";
import { API_URL } from "../api/specialRoute";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

export default function AdminSiteSettingsSection() {
  const [alertEnabled, setAlertEnabled] = useState(false);
  const [alertMessage, setAlertMessage] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [feedback, setFeedback] = useState<{ type: "success" | "error"; text: string } | null>(null);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    setIsLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/v1/settings/alert`, { credentials: "include" });
      if (!res.ok) throw new Error("Failed to fetch settings");
      const data = await res.json();
      setAlertEnabled(data.alert_enabled ?? false);
      setAlertMessage(data.alert_message ?? "");
    } catch (e) {
      console.error(e);
      setFeedback({ type: "error", text: "Failed to load current settings." });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    setFeedback(null);
    try {
      const res = await fetch(`${API_URL}/api/v1/settings/alert`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ alert_enabled: alertEnabled, alert_message: alertMessage }),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail?.message ?? "Failed to save settings");
      }
      setFeedback({ type: "success", text: "Settings saved successfully." });
    } catch (e: any) {
      setFeedback({ type: "error", text: e.message ?? "Failed to save settings." });
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="admin-section-content">
      <div className="admin-section-header">
        <h2>Site Settings</h2>
      </div>

      {isLoading ? (
        <div className="loading-state">Loading settings…</div>
      ) : (
        <div style={{ maxWidth: "600px", display: "flex", flexDirection: "column", gap: "1.5rem" }}>
          <div
            style={{
              background: "#f9fafb",
              border: "1px solid #e5e7eb",
              borderRadius: "0.75rem",
              padding: "1.5rem",
              display: "flex",
              flexDirection: "column",
              gap: "1.25rem",
            }}
          >
            <h3 style={{ margin: 0, fontSize: "1rem", fontWeight: 600 }}>Site-Wide Alert Banner</h3>
            <p style={{ margin: 0, color: "#6b7280", fontSize: "0.875rem" }}>
              When enabled, a popup will appear for all visitors on every page of the site.
            </p>

            {/* Toggle */}
            <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
              <button
                role="switch"
                aria-checked={alertEnabled}
                onClick={() => setAlertEnabled((v) => !v)}
                style={{
                  position: "relative",
                  width: "48px",
                  height: "26px",
                  borderRadius: "9999px",
                  border: "none",
                  cursor: "pointer",
                  background: alertEnabled ? "#2563eb" : "#d1d5db",
                  transition: "background 0.2s",
                  flexShrink: 0,
                }}
              >
                <span
                  style={{
                    position: "absolute",
                    top: "3px",
                    left: alertEnabled ? "25px" : "3px",
                    width: "20px",
                    height: "20px",
                    borderRadius: "50%",
                    background: "#fff",
                    transition: "left 0.2s",
                    boxShadow: "0 1px 3px rgba(0,0,0,0.2)",
                  }}
                />
              </button>
              <Label style={{ cursor: "pointer", userSelect: "none" }} onClick={() => setAlertEnabled((v) => !v)}>
                {alertEnabled ? "Alert is ON" : "Alert is OFF"}
              </Label>
            </div>

            {/* Message */}
            <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
              <Label htmlFor="alert-message">Alert Message</Label>
              <Textarea
                id="alert-message"
                value={alertMessage}
                onChange={(e) => setAlertMessage(e.target.value)}
                placeholder="e.g., SG is out of session for the summer. We will return in the fall!"
                rows={4}
                maxLength={1000}
              />
              <span style={{ fontSize: "0.75rem", color: "#9ca3af" }}>
                {alertMessage.length}/1000 characters
              </span>
            </div>
          </div>

          {feedback && (
            <div
              role="alert"
              style={{
                padding: "0.75rem 1rem",
                borderRadius: "0.5rem",
                fontSize: "0.875rem",
                fontWeight: 500,
                background: feedback.type === "success" ? "#f0fdf4" : "#fef2f2",
                color: feedback.type === "success" ? "#166534" : "#991b1b",
                border: `1px solid ${feedback.type === "success" ? "#86efac" : "#fca5a5"}`,
              }}
            >
              {feedback.text}
            </div>
          )}

          <div>
            <Button onClick={handleSave} disabled={isSaving}>
              {isSaving ? "Saving…" : "Save Settings"}
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}

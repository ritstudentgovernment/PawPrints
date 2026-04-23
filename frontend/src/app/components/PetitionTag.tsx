"use client";

import React from "react";

type PetitionTagType = {
  id?: number;
  name: string;
  description: string;
  color?: string;
};

export default function PetitionTag({ name, description, color }: PetitionTagType) {
  return (
    <div
      style={{
        backgroundColor: color || "#F26522",
        color: "#FFFFFF",
        padding: "4px 12px",
        borderRadius: "12px",
        fontSize: "0.875rem",
        fontWeight: "500",
        display: "inline-block",
        marginRight: "6px",
      }}
      title={description}
    >
      {name}
    </div>
  );
}
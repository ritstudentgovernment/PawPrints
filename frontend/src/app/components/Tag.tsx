"use client";

import React from "react";
import "./tag.css";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { TagType } from "./SidebarItem";


export default function Tag(t: TagType) {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const { replace } = useRouter();

  function handleClick(e: React.MouseEvent) {
    e.stopPropagation();

    const params = new URLSearchParams(searchParams);
    params.set("tag", t.name);
    replace(`${pathname}?${params.toString()}`);
  }

  return (
    <div
      className="tag"
      onClick={handleClick}
      style={{ cursor: "pointer" }}
    >
      {t.name}
    </div>
  );
}

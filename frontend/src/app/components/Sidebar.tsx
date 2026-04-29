import React, { useEffect, useState } from 'react'
import './sidebar.css'
import { usePathname, useRouter, useSearchParams } from 'next/navigation';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { TagType } from './SidebarItem';

export default function Sidebar({ tags }: { tags: TagType[] }) {
  const searchParams = useSearchParams();
  const pathname = usePathname();
  const { replace } = useRouter();
  const [selectedTag, setSelectedTag] = useState<string | undefined>(undefined);

  function getTagNameById(id?: string | null): string | undefined {
    if (!id) return undefined;
    const tag = tags.find((t) => t.id.toString() === id);
    return tag ? tag.name : undefined;
  }

  useEffect(() => {
    const tagFromUrl = searchParams.get('tag');
    setSelectedTag(getTagNameById(tagFromUrl));
  }, [searchParams, tags]);

function filterSearch(tag_id?: string, tag_name?: string) {
  const params = new URLSearchParams(searchParams.toString());

  if (tag_id) {
    params.set("tag", tag_id);
  } else {
    params.delete("tag");
  }

  // reset pagination + search
  params.delete("page");
  params.delete("query");

  replace(`${pathname}?${params.toString()}`);
  setSelectedTag(tag_name);
}

  try {
    return (
      <div className={`sidebar`}>
        <DropdownMenu>
          <DropdownMenuTrigger className="sidebar-trigger">
            {selectedTag || "All Tags"}
          </DropdownMenuTrigger>
          <DropdownMenuContent className='sidebar-dropdown'>
            Filter by
            <DropdownMenuItem
              key={"All Tags"}
              onClick={() => filterSearch(undefined, undefined)}
            >
              All Tags
            </DropdownMenuItem>
            {tags.map((item: TagType) => (
              <DropdownMenuItem
                key={item.name}
                onClick={() => filterSearch(item.id.toString(), item.name)}
              >
                {item.name}
              </DropdownMenuItem>
            ))}
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    )
  } catch (error) {
    console.log(error)
    return null;
  }
}

"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { useEffect, useState } from "react";
import { z } from "zod";
import './petitionform.css';
import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Check, ChevronsUpDown } from "lucide-react";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Input } from "@/components/ui/input";
import { API_URL } from "../api/specialRoute";
import { useRouter } from "next/navigation";
import { cn } from "@/lib/utils";


import dynamic from "next/dynamic";

const LexicalEditor = dynamic(() => import("../components/Petition/LexicalEditor"), { 
  ssr: false,
  loading: () => <div className="min-h-[200px] border rounded-md bg-gray-50 animate-pulse">Loading editor...</div>
});

const formSchema = z.object({
  title: z.string().min(3, "Title must be at least 3 characters long."),
  description: z.string().min(10, "Description must be at least 10 characters long."),
  tags: z.array(z.number()).optional(),
});

type PetitionFormValues = z.infer<typeof formSchema>;

export function PetitionForm({
  init_is_edit = false,
  init_petition_id,
  init_title,
  init_tags,
} : {
  init_is_edit?: boolean,
  init_petition_id?: number | null,
  init_title?: string | null,
  init_tags?: Array<string | number> | null
}) {
  const router = useRouter();

  const [availableTags, setAvailableTags] = useState<{ id: number, name: string }[]>([]);

  const form = useForm<PetitionFormValues>({
      resolver: zodResolver(formSchema),
      defaultValues: {
        title: init_title || "",
        description: "",
        tags: [],
      },
    });

    const [isReady, setIsReady] = useState(false);
    
    useEffect(() => {
      let mounted = true;
      
      async function loadInitial() {
        try {
          // Fetch tags
          const tagsRes = await fetch(`${API_URL}/api/v1/tags`);
          const tagsJson = await tagsRes.json();
          const fetchedTags = tagsJson.tags || [];
          if (!mounted) return;
          setAvailableTags(fetchedTags);
          
          // Map init_tags (names or ids) to numeric ids
          let mappedIds: number[] = [];
          if (init_tags && init_tags.length > 0) {
            mappedIds = init_tags
              .map((item) =>
                typeof item === "number"
                  ? item
                  : fetchedTags.find((t: any) => t.name === item)?.id
              )
              .filter((id): id is number => id !== undefined);
          }
          
          // Fetch description when editing
          let desc = "";
          if (init_is_edit && init_petition_id) {
            try {
              const descRes = await fetch(`${API_URL}/api/v1/petitions/${init_petition_id}/description`);
              const descJson = await descRes.json();
              desc = descJson.petition_description || "";
            } catch (err) {
              console.error("Failed to fetch description:", err);
            }
          }
          
          // Reset the form with fetched values (this ensures defaults are applied together)
          if (mounted) {
            form.reset({
              title: init_title || "",
              description: desc,
              tags: mappedIds,
            });
            setIsReady(true);
          }
        } catch (err) {
          console.error("Failed to load initial data:", err);
          if (mounted) setIsReady(true); // allow form to render even if fetch failed
        }
      }
      
      loadInitial();
      
      return () => {
        mounted = false;
      };
    }, [init_tags, init_is_edit, init_petition_id, init_title, form]);

  async function submitToServer(data: PetitionFormValues, isDraft: boolean) {
    try {
      // data.tags already stores tag IDs (numbers). Use them directly.
      const tagIds = (data.tags || []) as number[];
      console.log("Tag IDs to send:", tagIds);

      const payload = {
        title: data.title,
        description: data.description,
        is_draft: isDraft,
        tags: tagIds,
      };

      console.log("Final payload:", payload);
      

      let res = null;

      if (init_is_edit && init_petition_id) {
        res = await fetch(`${API_URL}/api/v1/petitions/${init_petition_id}`, {
          method: "PUT",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        });
      } else {
        res = await fetch(`${API_URL}/api/v1/petitions/create`, {
          method: "POST",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        });
      }


      if (!res.ok) {
        const err = await res.text();
        console.error("Backend error:", err);
        alert("Failed to create petition. Check console for details.");
        return;
      }

      alert(isDraft ? "Draft saved!" : "Petition published!");

      if (init_is_edit) {
        window.location.reload();
      } else {
        router.push("/profile");
      }

    } catch (err) {
      console.error("Submit error:", err);
      alert("Something went wrong.");
    }
  }

  if (!isReady) {
    return (
      <div className="form">
        <div className="p-4">Loading form...</div>
      </div>
    );
  }

  return (
    <div className="form">
      <Form {...form}>
        <form className="space-y-8">
          {/* Title */}
          <FormField
            control={form.control}
            name="title"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Petition Title</FormLabel>
                <FormControl>
                  <Input placeholder="Enter your petition title" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          {/* Description */}
          <FormField
            control={form.control}
            name="description"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Petition Description</FormLabel>
                <FormControl>
                  <LexicalEditor placeholderText="Describe your petition..." value={field.value} onChange={field.onChange} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          {/* Tags */}
          <FormField
            control={form.control}
            name="tags"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Petition Tags</FormLabel>
                <br />
                <FormControl>
                  <Popover>
                      <PopoverTrigger asChild className="tag-dropdown">
                      <Button
                        variant="outline"
                        role="combobox"
                        className="w-[300px] justify-between"
                      >
                        {field.value?.length
                          ? field.value
                              .map((id) => availableTags.find((t) => t.id === id)?.name ?? String(id))
                              .join(", ")
                          : "Select tags"}
                        <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-[300px] p-0">
                      <Command>
                        <CommandInput placeholder="Search tags..." />
                        <CommandList>
                          <CommandEmpty>No tags found.</CommandEmpty>
                          <CommandGroup>
                            {availableTags.map((tag) => (
                              <CommandItem
                                key={tag.id}
                                onSelect={() => {
                                  const newTags = field.value?.includes(tag.id)
                                    ? field.value.filter((t) => t !== tag.id)
                                    : [...(field.value || []), tag.id];
                                  field.onChange(newTags);
                                }}
                              >
                                <Check
                                  className={cn(
                                    "mr-2 h-4 w-4",
                                    field.value?.includes(tag.id)
                                      ? "opacity-100"
                                      : "opacity-0"
                                  )}
                                />
                                {tag.name}
                              </CommandItem>
                            ))}
                          </CommandGroup>
                        </CommandList>
                      </Command>
                    </PopoverContent>
                  </Popover>
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          {/* Buttons */}
          <div className="flex gap-4">
            <Button
              className="draft-btn"
              type="button"
              variant="secondary"
              onClick={form.handleSubmit((d) => submitToServer(d, true))}
            >
              Save as Draft
            </Button>

            <Button
              className="submit-btn"
              type="button"
              variant="highlight"
              onClick={form.handleSubmit((d) => submitToServer(d, false))}
            >
              Publish
            </Button>
          </div>
        </form>
      </Form>
    </div>
  );
}

"use client";

import { useMemo } from "react";
import DOMPurify from "isomorphic-dompurify";
import { cn } from "@/lib/utils";

import { LexicalComposer } from "@lexical/react/LexicalComposer";
import { ContentEditable } from "@lexical/react/LexicalContentEditable";
import { RichTextPlugin } from "@lexical/react/LexicalRichTextPlugin";
import { LexicalErrorBoundary } from "@lexical/react/LexicalErrorBoundary";
import { AutoLinkNode, LinkNode } from "@lexical/link";
import { HeadingNode, QuoteNode } from "@lexical/rich-text";
import { ListNode, ListItemNode } from "@lexical/list";
import { useLexicalComposerContext } from "@lexical/react/LexicalComposerContext";
import { useEffect } from "react";
import { $getRoot } from "lexical";
import { $generateNodesFromDOM } from "@lexical/html";
import { ClickableLinkPlugin } from '@lexical/react/LexicalClickableLinkPlugin';
import { AutoLinkPlugin } from '@lexical/react/LexicalAutoLinkPlugin';

import { ImageNode } from "./ImageNode";
import { MATCHERS } from "./matchers";
import EditorTheme from "./EditorTheme";
import './editor.css';

function isValidLexicalJson(str: string) {
  if (!str || typeof str !== "string") return false;
  const trimmed = str.trim();
  
  // Quick check for Lexical structure
  if (!(trimmed.startsWith("{") && trimmed.includes('"root"'))) return false;
  
  try {
    const parsed = JSON.parse(trimmed);
    return parsed && typeof parsed === 'object' && 'root' in parsed;
  } catch (e) {
    return false;
  }
}

function decodeHtml(html: string) {
  const txt = document.createElement("textarea");
  txt.innerHTML = html;
  return txt.value;
}



function ViewerUpdatePlugin({ content }: { content: string }) {
  const [editor] = useLexicalComposerContext();

  useEffect(() => {
    editor.update(() => {
      // 1. Check if it's JSON
      let isJson = false;
      try {
        const parsed = JSON.parse(content);
        if (parsed && parsed.root) isJson = true;
      } catch (e) {}

      // 2. If JSON, load it directly
      if (isJson) {
         const newState = editor.parseEditorState(content);
         editor.setEditorState(newState);
         return;
      }

      // 3. If HTML/Text, parse and insert
      const parser = new DOMParser();
      const dom = parser.parseFromString(content, "text/html");
      const nodes = $generateNodesFromDOM(editor, dom);

      const root = $getRoot();
      root.clear();
      root.append(...nodes);
    });
  }, [content, editor]); // <--- Runs every time 'content' changes

  return null;
}

export default function LexicalViewer({ 
  content, 
  className 
}: { 
  content: string; 
  className?: string 
}) {
  
  const normalizedContent = content?.trim() || "";
  const isJson = useMemo(() => isValidLexicalJson(normalizedContent), [normalizedContent]);

  // for legacy HTML content, sanitize
  if (!isJson) {
    let cleanHtml = "";
    
    if (typeof window !== 'undefined') {
        try {
            const decoded = decodeHtml(content || "");
            
            // Sanitize: Keeps bold/divs/lists, Remove <meta>/scripts
            cleanHtml = DOMPurify.sanitize(decoded, {
                FORBID_TAGS: ['meta', 'style', 'script', 'title', 'link'],
                ADD_ATTR: ['target']
            });
        } catch (e) {
            cleanHtml = content;
        }
    }

    return (
      <div 
        className={cn(
          "prose prose-sm max-w-none dark:prose-invert [&>div]:mb-4 text-gray-800 dark:text-gray-200",
          "break-words min-h-[20px]", 
          className
        )}
        dangerouslySetInnerHTML={{ __html: cleanHtml }} 
      />
    );
  }

  const initialConfig = {
    namespace: "Viewer",
    editable: false,
    theme: EditorTheme,
    onError: (e: any) => console.error(e),
    editorState: normalizedContent,
    nodes: [
        ImageNode, 
        AutoLinkNode, 
        LinkNode, 
        HeadingNode, 
        QuoteNode, 
        ListNode, 
        ListItemNode
    ],
  };

  return (
    <div className={cn("relative min-h-[20px]", className)}>
      <LexicalComposer initialConfig={initialConfig}>
        <RichTextPlugin
          contentEditable={<ContentEditable className="outline-none" />}
          placeholder={null}
          ErrorBoundary={LexicalErrorBoundary}
        />

        <ViewerUpdatePlugin content={normalizedContent} />
        
        <ClickableLinkPlugin />
        <AutoLinkPlugin matchers={MATCHERS} />
      </LexicalComposer>
    </div>
  );
}
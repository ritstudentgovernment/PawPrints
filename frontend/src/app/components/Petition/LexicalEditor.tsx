"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { LexicalComposer } from "@lexical/react/LexicalComposer";
import { RichTextPlugin } from "@lexical/react/LexicalRichTextPlugin";
import { ContentEditable } from "@lexical/react/LexicalContentEditable";
import { OnChangePlugin } from "@lexical/react/LexicalOnChangePlugin";
import { AutoLinkNode, LinkNode, TOGGLE_LINK_COMMAND, $isLinkNode, $createLinkNode } from "@lexical/link";
import { useLexicalComposerContext } from "@lexical/react/LexicalComposerContext";
import { LexicalErrorBoundary } from "@lexical/react/LexicalErrorBoundary";
import { AutoLinkPlugin } from '@lexical/react/LexicalAutoLinkPlugin';
import { ClickableLinkPlugin } from '@lexical/react/LexicalClickableLinkPlugin';
import { LinkPlugin } from "@lexical/react/LexicalLinkPlugin"
import { ListPlugin } from "@lexical/react/LexicalListPlugin"
import { ImageNode, $createImageNode } from "./ImageNode";
import { AutoFocusPlugin } from "@lexical/react/LexicalAutoFocusPlugin";

import { 
    $getRoot, 
    $createParagraphNode, 
    $createTextNode, 
    $isElementNode,
    $isDecoratorNode,
    $insertNodes,
    FORMAT_TEXT_COMMAND, 
    $getSelection, 
    $isRangeSelection, 
    FORMAT_ELEMENT_COMMAND, 
} from "lexical";

import {
  INSERT_ORDERED_LIST_COMMAND,
  INSERT_UNORDERED_LIST_COMMAND,
  ListItemNode,
  ListNode,
  REMOVE_LIST_COMMAND,
} from "@lexical/list";

import { $setBlocksType } from "@lexical/selection";
import { $createHeadingNode, $createQuoteNode, HeadingNode, HeadingTagType, QuoteNode } from "@lexical/rich-text";

import { MATCHERS } from "./matchers";

import { cn } from "@/lib/utils";
import EditorTheme from "./EditorTheme";
import './editor.css';

import { $generateNodesFromDOM } from "@lexical/html";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@radix-ui/react-dropdown-menu";
import { LinkDialog } from "./LinkDialog";
import { API_URL } from "@/app/api/specialRoute";

export const isLexicalEmpty = (jsonString: string): boolean => {
  if (!jsonString) return true;
  
  // Handle "Plain Text" case (Legacy data or simple inputs)
  if (!jsonString.trim().startsWith("{")) {
    return jsonString.trim().length === 0;
  }

  try {
    const data = JSON.parse(jsonString);
    const root = data.root;

    // Recursive function to find ANY content
    const hasContent = (node: any): boolean => {
      // If it's a Text Node, check if it has actual characters
      if (node.type === "text") {
        return node.text && node.text.trim().length > 0;
      }

      // If it's a Decorator Node (Image, Video, Tweet, etc.)
      // These types don't have children but represent content.
      // Add any custom node types you use here.
      if (["image", "horizontal-rule", "tweet", "youtube"].includes(node.type)) {
        return true;
      }

      // If it's a Block (Paragraph, Heading, List, etc.), check its children
      if (node.children && Array.isArray(node.children)) {
        return node.children.some((child: any) => hasContent(child));
      }

      return false;
    };

    return !hasContent(root);
    
  } catch (e) {
    return true;
  }
};

// Helper to detect if string is Lexical JSON
const isJsonString = (str: string) => {
  try {
    const result = JSON.parse(str);
    return result && typeof result === "object" && result.root;
  } catch (e) {
    return false;
  }
};


function UpdatePlugin({ value }: { value: string }) {
  const [editor] = useLexicalComposerContext();

  useEffect(() => {
    // If the editor has focus, the USER is driving the change.
    // We should ignore the 'value' prop unless it is explicitly empty (Clear).
    // Stop the loop
    const isFocused = editor.getRootElement() === document.activeElement;
    if (isFocused && value !== "") {
        return; 
    }

    editor.update(() => {
      const root = $getRoot();

      // CASE 1: Empty (Clear)
      if (!value) {
        root.clear();
        root.append($createParagraphNode());
        return;
      }

      // CASE 2: Populate from JSON (Lexical State)
      if (isJsonString(value)) {
        const newState = editor.parseEditorState(value);
        editor.setEditorState(newState);
        return;
      }

      // CASE 3: Populate from HTML/Text
      const parser = new DOMParser();
      const dom = parser.parseFromString(value, "text/html");
      const nodes = $generateNodesFromDOM(editor, dom);

      root.clear();

      const blockNodes = [];
      let currentParagraph = null;

      for (const node of nodes) {
        if ($isElementNode(node) || $isDecoratorNode(node)) {
          if (currentParagraph) {
            blockNodes.push(currentParagraph);
            currentParagraph = null;
          }
          blockNodes.push(node);
        } else {
          // Wrap text/linebreaks in a paragraph
          if (!currentParagraph) {
            currentParagraph = $createParagraphNode();
          }
          currentParagraph.append(node);
        }
      }
      if (currentParagraph) blockNodes.push(currentParagraph);

      if (blockNodes.length > 0) {
        root.append(...blockNodes);
      } else {
        root.append($createParagraphNode());
      }
    });

  }, [value, editor]);

  return null;
}


const blockOptions = [
  { name: "Normal", value: "paragraph" },
  { name: "Heading 1", value: "h1" },
  { name: "Heading 2", value: "h2" },
  { name: "Heading 3", value: "h3" },
  { name: "Numbered List", value: "number" },
  { name: "Bullet List", value: "bullet" },
  { name: "Quote", value: "quote" },
];

function ToolbarPlugin({ onImageUpload }: { onImageUpload: () => void }) {
    const [editor] = useLexicalComposerContext();
    const [isBold, setIsBold] = useState(false);
    const [isItalic, setIsItalic] = useState(false);
    const [isUnderline, setIsUnderline] = useState(false);
    const [isLeftAlign, setIsLeftAlign] = useState(false);
    const [isCenterAlign, setIsCenterAlign] = useState(false);
    const [isRightAlign, setIsRightAlign] = useState(false);
    const [isJustifyAlign, setIsJustifyAlign] = useState(false);
    const [isLink, setIsLink] = useState(false);
    
    const [currentBlockType, setCurrentBlockType] = useState<string>("paragraph");

    const selectedOptionName = blockOptions.find((opt) => opt.value === currentBlockType)?.name || "Normal";

    useEffect(() => {
        return editor.registerUpdateListener(({ editorState }) => {
            editorState.read(() => {
                const selection = $getSelection();

                if ($isRangeSelection(selection)) {
                    setIsBold(selection.hasFormat("bold"));
                    setIsItalic(selection.hasFormat("italic"));
                    setIsUnderline(selection.hasFormat("underline"));

                    const anchorNode = selection.anchor.getNode();

                    let element = anchorNode.getKey() === "root"
                        ? anchorNode
                        : anchorNode.getTopLevelElementOrThrow();
                        
                    if ($isElementNode(element)) {
                        const elementFormat = element.getFormatType(); 
                        
                        setIsLeftAlign(elementFormat === "left" || elementFormat === "");
                        setIsCenterAlign(elementFormat === "center");
                        setIsRightAlign(elementFormat === "right");
                        setIsJustifyAlign(elementFormat === "justify");
                    } 

                    const parent = anchorNode.getParent();
                    
                    if ($isLinkNode(parent) || $isLinkNode(anchorNode)) {
                        setIsLink(true);
                    } else {
                        setIsLink(false);
                    }
                }
            });
        });
    }, [editor]);

    const formatBlock = useCallback(
      (blockType: string) => {
        if (blockType === "bullet") {
          if (currentBlockType !== "bullet") {
            editor.dispatchCommand(INSERT_UNORDERED_LIST_COMMAND, undefined);
          } else {
            editor.dispatchCommand(REMOVE_LIST_COMMAND, undefined);
          }
          setCurrentBlockType("bullet");
          return;
        }
        
        if (blockType === "number") {
          if (currentBlockType !== "number") {
            editor.dispatchCommand(INSERT_ORDERED_LIST_COMMAND, undefined);
          } else {
            editor.dispatchCommand(REMOVE_LIST_COMMAND, undefined);
          }
          setCurrentBlockType("number");
          return;
        }

        editor.update(() => {
          const selection = $getSelection();
          if ($isRangeSelection(selection)) {
            if (blockType === "paragraph") {
              $setBlocksType(selection, () => $createParagraphNode());
            } else if (blockType === "quote") {
              $setBlocksType(selection, () => $createQuoteNode());
            } else if (["h1", "h2", "h3"].includes(blockType)) {
              $setBlocksType(selection, () => $createHeadingNode(blockType as HeadingTagType));
            }
          }
        });
        setCurrentBlockType(blockType);
      },
      [editor, currentBlockType]
    );
  
    const format = (formatType: any, value: any) => {
        editor.dispatchCommand(formatType, value);
    };

    const insertLink = useCallback(() => {
        if (!editor) return;

        editor.update(() => {
        const selection = $getSelection();

        if ($isRangeSelection(selection) && !selection.isCollapsed()) {
            const url = window.prompt("Enter URL:", "https://");
            if (!url) return;

            editor.dispatchCommand(TOGGLE_LINK_COMMAND, url);

        } else if ($isRangeSelection(selection) && selection.isCollapsed()) {
            const text = window.prompt("Enter Link Text:", "Click Here");
            const url = window.prompt("Enter URL:", "https://");
            
            if (!text || !url) return;

            const linkNode = $createLinkNode(url);
            const textNode = $createTextNode(text);
            linkNode.append(textNode);
            
            selection.insertNodes([linkNode]);
            textNode.select();
        }
        });
    }, [editor]);

    return (
        <div className="toolbar">
          <DropdownMenu>
            <DropdownMenuTrigger className="toolbar-dropdown-trigger">
              {/* 1. The Active Icon and Name (Reusing your layout) */}
              <div className="icon-text-container">
                <i className={`block-${currentBlockType}`} />
                <span className="text">{selectedOptionName}</span>
              </div>

              {/* 2. The Chevron SVG */}
              <svg 
                className="chevron-down" 
                width="16" 
                height="16" 
                viewBox="0 0 24 24" 
                fill="none" 
                stroke="currentColor" 
                strokeWidth="2" 
                strokeLinecap="round" 
                strokeLinejoin="round"
              >
                <path d="M6 9l6 6 6-6" />
              </svg>
            </DropdownMenuTrigger>
            
            <DropdownMenuContent className="toolbar-dropdown-content">
              <div className="toolbar-dropdown-label">
                Turn into
              </div>
              {blockOptions.map((item) => (
                <DropdownMenuItem
                  key={item.value}
                  onClick={() => formatBlock(item.value)}
                  className="toolbar-dropdown-item"
                >
                  {
                    <div className="icon-text-container">
                      <i className={`block-${item.value}`}/>
                      <span className="text">{item.name}</span>
                    </div>
                  }
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>
          <button
              onClick={() => {
                  format(FORMAT_TEXT_COMMAND, "bold");
              }}
              className={"toolbar-item spaced " + (isBold ? "active" : "")}
              title={ "Bold"}
              type="button"
          >
              <i className="format bold" />
          </button>
          <button
              onClick={() => {
                  format(FORMAT_TEXT_COMMAND, "italic");
              }}
              className={"toolbar-item spaced " + (isItalic ? "active" : "")}
              title={"Italic "}
              type="button"
          >
              <i className="format italic" />
          </button>
          <button
              onClick={() => {
                  format(FORMAT_TEXT_COMMAND, "underline");
              }}
              className={"toolbar-item spaced " + (isUnderline ? "active" : "")}
              title={"Underline"}
              type="button"
          >
              <i className="format underline" />
          </button>
          <button
              type="button"
              onClick={() => {
                  format(FORMAT_ELEMENT_COMMAND, "left");
              }}
              className={"toolbar-item spaced" + (isLeftAlign ? " active" : "")}
              title={"Left Align"}
          >
              <i className="format left-align" />
          </button>
          <button
              type="button"
              onClick={() => {
                  format(FORMAT_ELEMENT_COMMAND, "center");
              }}
              className={"toolbar-item spaced" + (isCenterAlign ? " active" : "")}
              title={"Center Align"}
          >
              <i className="format center-align" />
          </button>
          <button
              type="button"
              onClick={() => {
                  format(FORMAT_ELEMENT_COMMAND, "right");
              }}
              className={"toolbar-item spaced" + (isRightAlign ? " active" : "")}
              title={"Right Align"}
          >
              <i className="format right-align" />
          </button>
          <button
              type="button"
              onClick={() => {
                  format(FORMAT_ELEMENT_COMMAND, "justify");
              }}
              className={"toolbar-item spaced" + (isJustifyAlign ? " active" : "")}
              title={"Justify Align"}
          >
              <i className="format justify-align" />
          </button>

          <LinkDialog editor={editor} isLink={isLink}/>

          {/* <button
              type="button"
              onClick={onImageUpload}
              className="px-2 py-1 text-sm border border-blue-200 bg-blue-50 text-blue-600 rounded hover:bg-blue-100"
          >
              + Image
          </button> */}
        </div>
    );
}

interface EditorProps {
    placeholderText?: string;
    value: string; // Can be Plain Text OR JSON String
    onChange: (val: string) => void;
    className?: string;
}

export default function LexicalEditor({ placeholderText="Description", value, onChange, className }: EditorProps) {
  
    const initialConfig = useMemo(() => {
        return {
            namespace: "MyNextEditor",
            editorState: () => {
                const root = $getRoot();
                // Prevent duplicate appending on re-renders
                if (root.getFirstChild() === null) {
                    const paragraph = $createParagraphNode();
                    paragraph.append($createTextNode(value || ""));
                    root.append(paragraph);
                }
            },
            theme: EditorTheme,
            nodes: [
              ImageNode, 
              AutoLinkNode, 
              LinkNode, 
              HeadingNode,
              QuoteNode,
              ListNode,
              ListItemNode
            ],
            onError: (error: any) => console.error(error),
        };
    }, []);

    const fileInputRef = useRef<HTMLInputElement>(null);
    const editorRef = useRef<any>(null);

    const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        
        if (file && editorRef.current) {
            const formData = new FormData();
            formData.append("file", file);

            try {
                const response = await fetch(`${API_URL}/api/v1/images/upload`, {
                  method: 'POST',
                  credentials: 'include',
                  body: formData
                });

                if (!response.ok) {
                  const data = await response.json()
                  throw new Error(`Upload failed ${data.message}`);
                }

                const data = await response.json();
                const minioUrl = data.uri;

                editorRef.current.update(() => {
                    const imageNode = $createImageNode({ 
                        src: minioUrl, 
                        altText: file.name 
                    });
                    
                    $insertNodes([imageNode]); 
                });

            } catch (error) {
                console.error("Failed to upload image:", error);
                alert("Failed to upload image. Check console for details.");
            } finally {
                if (fileInputRef.current) fileInputRef.current.value = "";
            }
        }
    };

  return (
    <div className={cn("relative flex flex-col w-full border border-gray-200 rounded-md shadow-sm bg-white", className)}>
        <LexicalComposer initialConfig={initialConfig}>
            {/* Capture Editor Reference for external actions */}
            <EditorRefPlugin editorRef={editorRef} />
            
            <ToolbarPlugin onImageUpload={() => fileInputRef.current?.click()} />
            
            <div className="relative min-h-[200px] p-4 bg-background">
            <RichTextPlugin
                contentEditable={<ContentEditable className="lexical-editor-root outline-none h-full min-h-[150px] resize-none" />}
                placeholder={<div className="absolute top-4 left-4 text-muted-foreground pointer-events-none">{placeholderText}</div>}
                ErrorBoundary={LexicalErrorBoundary}
            />

            <ListPlugin />
            <LinkPlugin />
            <ClickableLinkPlugin />
            <AutoLinkPlugin matchers={MATCHERS} />
            <AutoFocusPlugin />

            <OnChangePlugin
                onChange={(editorState) => {
                const jsonString = JSON.stringify(editorState.toJSON());
                onChange(jsonString);
                }}
            />

            <UpdatePlugin value={value} />
            </div>
        </LexicalComposer>

      {/* Hidden File Input for Uploads */}
      <input
        type="file"
        ref={fileInputRef}
        className="hidden"
        accept="image/*"
        onChange={handleImageUpload}
      />
    </div>
  );
}

// Helper to expose editor instance to parent ref
function EditorRefPlugin({ editorRef }: { editorRef: any }) {
    const [editor] = useLexicalComposerContext();
    useEffect(() => {
        editorRef.current = editor;
    }, [editor, editorRef]);
    return null;
}
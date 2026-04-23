import React, { useState } from 'react';
import { 
  $getSelection, 
  $isRangeSelection, 
  $createTextNode, 
  LexicalEditor 
} from 'lexical';
import { $createLinkNode, TOGGLE_LINK_COMMAND } from '@lexical/link';
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle, 
  DialogFooter, 
  DialogTrigger, 
  DialogClose 
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

interface LinkDialogProps {
  editor: LexicalEditor;
  isLink: boolean;
}

export function LinkDialog({ editor, isLink }: LinkDialogProps) {
  const [url, setUrl] = useState<string>("https://");
  const [linkText, setLinkText] = useState<string>("");
  const [hasSelection, setHasSelection] = useState<boolean>(false);
  const [isOpen, setIsOpen] = useState<boolean>(false);

  const handleOpenChange = (open: boolean) => {
    setIsOpen(open);
    if (open && editor) {
      editor.getEditorState().read(() => {
        const selection = $getSelection();
        if ($isRangeSelection(selection)) {
          const isCollapsed = selection.isCollapsed();
          setHasSelection(!isCollapsed);
          setLinkText(!isCollapsed ? selection.getTextContent() : "");
        }
      });
    }
  };

  const handleConfirm = () => {
    if (!editor || !url) return;
    editor.update(() => {
      const selection = $getSelection();
      if ($isRangeSelection(selection)) {
        if (hasSelection) {
          editor.dispatchCommand(TOGGLE_LINK_COMMAND, url);
        } else {
          const linkNode = $createLinkNode(url);
          const textNode = $createTextNode(linkText || "Click Here");
          linkNode.append(textNode);
          selection.insertNodes([linkNode]);
        }
      }
    });
    setIsOpen(false);
    setUrl("https://"); 
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleOpenChange}>
      <DialogTrigger asChild>
        <button
          type="button"
          className={"toolbar-item spaced" + (isLink ? " active" : "")}
          title={"Insert Link"}
        >
          <i className="format link" />
        </button>
      </DialogTrigger>
      
      {/* Reduced max-width and internal padding to keep it slim */}
      <DialogContent className="sm:max-w-[350px] p-6 gap-6">
        <DialogHeader>
            <DialogTitle className="text-xl font-semibold">Insert Link</DialogTitle>
        </DialogHeader>
        
        <div className="flex flex-col gap-5">
            {!hasSelection && (
            <div className="grid w-full items-center gap-2">
                <Label htmlFor="linkText" className="text-sm font-medium">Link Text</Label>
                <Input
                id="linkText"
                className="h-9"
                value={linkText}
                onChange={(e) => setLinkText(e.target.value)}
                placeholder="Display text"
                />
            </div>
            )}
            
            <div className="grid w-full items-center gap-2">
            <Label htmlFor="linkUrl" className="text-sm font-medium">URL</Label>
            <Input
                id="linkUrl"
                className="h-9"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://example.com"
            />
            </div>
        </div>

        <DialogFooter className="flex flex-row justify-end gap-3 mt-4">
            <DialogClose asChild>
            <Button variant="ghost" className="h-10 px-4">
                Cancel
            </Button>
            </DialogClose>
            <Button 
            onClick={handleConfirm} 
            disabled={!url}
            // Force visibility with strong orange and white text
            className="h-10 px-6 bg-[#f97316] hover:bg-[#ea580c] text-white font-bold shadow-sm"
            >
            Insert Link
            </Button>
        </DialogFooter>
        </DialogContent>
    </Dialog>
  );
}
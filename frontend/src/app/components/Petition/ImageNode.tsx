import { 
  DecoratorNode, 
  NodeKey, 
  SerializedLexicalNode, 
  Spread 
} from "lexical";
import { ReactNode } from "react";

export type SerializedImageNode = Spread<
  {
    src: string;
    altText: string;
  },
  SerializedLexicalNode
>;

export class ImageNode extends DecoratorNode<ReactNode> {
  __src: string;
  __altText: string;

  static getType(): string { return "image"; }

  static clone(node: ImageNode): ImageNode {
    return new ImageNode(node.__src, node.__altText, node.__key);
  }

  static importJSON(serializedNode: SerializedImageNode): ImageNode {
    return new ImageNode(serializedNode.src, serializedNode.altText);
  }

  constructor(src: string, altText: string, key?: NodeKey) {
    super(key);
    this.__src = src;
    this.__altText = altText;
  }

  exportJSON(): SerializedImageNode {
    return {
      src: this.__src,
      altText: this.__altText,
      type: "image",
      version: 1,
    };
  }

  createDOM(): HTMLElement {
    return document.createElement("span");
  }

  updateDOM(): false {
    return false;
  }

  decorate(): ReactNode {
    return (
      <span className="flex justify-center w-full my-6">
        <img
          src={this.__src}
          alt={this.__altText}
          className="w-full max-w-2xl max-h-96 rounded-md border border-slate-200 object-contain bg-slate-50"
        />
      </span>
    );
  }
}

export function $createImageNode({ src, altText }: { src: string; altText: string }): ImageNode {
  return new ImageNode(src, altText);
}
import { QuartzTransformerPlugin } from "../types"
import { Root, Element } from "hast"
import { visit } from "unist-util-visit"

// Silver Family Archive: show each photo's alt text as a visible caption.
// A paragraph holding nothing but one image becomes <figure><img><figcaption>alt</figcaption></figure>.
export const FigureCaptions: QuartzTransformerPlugin = () => {
  return {
    name: "FigureCaptions",
    htmlPlugins() {
      return [
        () => (tree: Root) => {
          visit(tree, "element", (node: Element) => {
            if (node.tagName !== "p") return
            const kids = node.children.filter(
              (c) => !(c.type === "text" && c.value.trim() === ""),
            )
            if (kids.length !== 1) return
            const img = kids[0]
            if (img.type !== "element" || img.tagName !== "img") return
            const alt = String(img.properties?.alt ?? "").trim()
            if (!alt || /^File:/i.test(alt) || /\.(jpe?g|png|gif|webp)$/i.test(alt)) return
            node.tagName = "figure"
            node.properties = { className: ["photo"] }
            node.children = [
              img,
              { type: "element", tagName: "figcaption", properties: {}, children: [{ type: "text", value: alt }] },
            ]
          })
        },
      ]
    },
  }
}

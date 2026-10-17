import { PageLayout, SharedLayout } from "./quartz/cfg"
import * as Component from "./quartz/components"

// components shared across all pages
export const sharedPageComponents: SharedLayout = {
  head: Component.Head(),
  header: [],
  afterBody: [],
  footer: Component.Footer({
    links: {
      GitHub: "https://github.com/jackyzha0/quartz",
      "Discord Community": "https://discord.gg/cRFFHYye7t",
    },
  }),
}

// components for pages that display a single page (e.g. a single note)
export const defaultContentPageLayout: PageLayout = {
  beforeBody: [
    Component.ConditionalRender({
      component: Component.Breadcrumbs(),
      condition: (page) => page.fileData.slug !== "index",
    }),
    Component.ArticleTitle(),
    Component.ContentMeta(),
    Component.TagList(),
  ],
  left: [
    Component.PageTitle(),
    Component.MobileOnly(Component.Spacer()),
    Component.Flex({
      components: [
        {
          Component: Component.Search(),
          grow: true,
        },
        { Component: Component.Darkmode() },
        { Component: Component.ReaderMode() },
      ],
    }),
    Component.Explorer({
      // people in family order, then each folder's pages by the first year in their title
      sortFn: (a, b) => {
        const order = ["Clifford-Marking-Silver", "Gladys-Silver", "Christopher-Silver", "David-Silver",
          "Anthea-Silver", "Jago-Silver", "Places", "Biography", "A-Topsham-Childhood",
          "UK", "Cornwall", "Wales", "Ireland", "France", "People", "India", "Vietnam", "Canada", "USA", "Letters"]
        // no named helpers here: the function is serialised, and esbuild would wrap them in __name()
        const r = [a, b].map((n) => {
          const i = order.indexOf(n.slugSegment)
          if (i >= 0) return i - 1000
          const m = n.displayName.match(/(1[6-9]\d\d|20\d\d)/)
          return m ? parseInt(m[1]) : 9999
        })
        const d = r[0] - r[1]
        return d !== 0 ? d : a.displayName.localeCompare(b.displayName, undefined, { numeric: true, sensitivity: "base" })
      },
    }),
  ],
  right: [
    Component.Graph(),
    Component.DesktopOnly(Component.TableOfContents()),
    Component.Backlinks(),
  ],
}

// components for pages that display lists of pages  (e.g. tags or folders)
export const defaultListPageLayout: PageLayout = {
  beforeBody: [Component.Breadcrumbs(), Component.ArticleTitle(), Component.ContentMeta()],
  left: [
    Component.PageTitle(),
    Component.MobileOnly(Component.Spacer()),
    Component.Flex({
      components: [
        {
          Component: Component.Search(),
          grow: true,
        },
        { Component: Component.Darkmode() },
      ],
    }),
    Component.Explorer({
      // people in family order, then each folder's pages by the first year in their title
      sortFn: (a, b) => {
        const order = ["Clifford-Marking-Silver", "Gladys-Silver", "Christopher-Silver", "David-Silver",
          "Anthea-Silver", "Jago-Silver", "Places", "Biography", "A-Topsham-Childhood",
          "UK", "Cornwall", "Wales", "Ireland", "France", "People", "India", "Vietnam", "Canada", "USA", "Letters"]
        // no named helpers here: the function is serialised, and esbuild would wrap them in __name()
        const r = [a, b].map((n) => {
          const i = order.indexOf(n.slugSegment)
          if (i >= 0) return i - 1000
          const m = n.displayName.match(/(1[6-9]\d\d|20\d\d)/)
          return m ? parseInt(m[1]) : 9999
        })
        const d = r[0] - r[1]
        return d !== 0 ? d : a.displayName.localeCompare(b.displayName, undefined, { numeric: true, sensitivity: "base" })
      },
    }),
  ],
  right: [],
}

import { QuartzConfig } from "./quartz/cfg"
import * as Plugin from "./quartz/plugins"

/**
 * Quartz 4 Configuration
 * Silver Family Archive
 */
const config: QuartzConfig = {
  configuration: {
    pageTitle: "Silver Family Archive",
    pageTitleSuffix: " — Silver Family Archive",
    enableSPA: true,
    enablePopovers: true,
    analytics: {
      provider: "umami",
    },
    locale: "en-GB",
    baseUrl: "jagosilver.github.io/silver-family-archive",
    ignorePatterns: ["private", "templates", ".obsidian"],
    defaultDateType: "modified",
    theme: {
      fontOrigin: "googleFonts",
      cdnCaching: true,
      typography: {
        header: "Playfair Display",
        body: "Source Serif 4",
        code: "IBM Plex Mono",
      },
      colors: {
        lightMode: {
          light: "#f5f0e8",
          lightgray: "#e0d8cc",
          gray: "#a09080",
          darkgray: "#3a3028",
          dark: "#1a1008",
          secondary: "#6b4c2a",
          tertiary: "#a07848",
          highlight: "rgba(107, 76, 42, 0.10)",
          textHighlight: "#d4b89688",
        },
        darkMode: {
          light: "#1a1510",
          lightgray: "#2e2620",
          gray: "#6a5a48",
          darkgray: "#d8c8b8",
          dark: "#f0e8d8",
          secondary: "#c89060",
          tertiary: "#a07848",
          highlight: "rgba(200, 144, 96, 0.12)",
          textHighlight: "#6b4c2a88",
        },
      },
    },
  },
  plugins: {
    transformers: [
      Plugin.FrontMatter(),
      Plugin.CreatedModifiedDate({
        priority: ["frontmatter", "git", "filesystem"],
      }),
      Plugin.SyntaxHighlighting({
        theme: {
          light: "github-light",
          dark: "github-dark",
        },
        keepBackground: false,
      }),
      Plugin.ObsidianFlavoredMarkdown({ enableInHtmlEmbed: false }),
      Plugin.GitHubFlavoredMarkdown(),
      Plugin.TableOfContents(),
      Plugin.CrawlLinks({ markdownLinkResolution: "shortest" }),
      Plugin.Description(),
      Plugin.Latex({ renderEngine: "katex" }),
    ],
    filters: [Plugin.RemoveDrafts()],
    emitters: [
      Plugin.AliasRedirects(),
      Plugin.ComponentResources(),
      Plugin.ContentPage(),
      Plugin.FolderPage(),
      Plugin.TagPage(),
      Plugin.ContentIndex({
        enableSiteMap: true,
        enableRSS: true,
      }),
      Plugin.Assets(),
      Plugin.Static(),
      Plugin.Favicon(),
      Plugin.NotFoundPage(),
    ],
  },
}

export default config

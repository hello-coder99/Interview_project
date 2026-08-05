import { normalizeWebsiteUrl } from "./utils.js";

export function buildToolDeclarations(Type) {
  return [
    {
      functionDeclarations: [
        {
          name: "openWebsite",
          description: "Open a website in the user's browser when the user asks for it.",
          parameters: {
            type: Type.OBJECT,
            properties: {
              url: {
                type: Type.STRING,
                description: "The website URL or domain to open.",
              },
              target: {
                type: Type.STRING,
                enum: ["new_tab", "current_tab"],
                description: "Where to open the website. Use new_tab unless the user asks otherwise.",
              },
            },
            required: ["url"],
          },
        },
      ],
    },
  ];
}

export function executeToolCall(functionCall) {
  if (functionCall.name !== "openWebsite") {
    return {
      ok: false,
      error: `Unknown tool: ${functionCall.name}`,
    };
  }

  try {
    const args = functionCall.args || {};
    const url = normalizeWebsiteUrl(args.url);
    const target = args.target === "current_tab" ? "_self" : "_blank";
    const opened = window.open(url, target, "noopener,noreferrer");

    return {
      ok: Boolean(opened) || target === "_self",
      url,
      target: args.target === "current_tab" ? "current_tab" : "new_tab",
      note: opened ? "Opened." : "Popup may have been blocked.",
    };
  } catch (error) {
    return {
      ok: false,
      error: error.message,
    };
  }
}

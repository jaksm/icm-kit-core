// The page side of "publish a page": builders inline this file, and pages reach the host's
// store ('db') and connectors ('mcp') only through window.icmHost, so no page names a harness.
// Another adapter ships its own file with the same shape: use(name) -> capability or null.
window.icmHost = {use: async n => (window.claude && window.claude.use ? window.claude.use(n) : null)};

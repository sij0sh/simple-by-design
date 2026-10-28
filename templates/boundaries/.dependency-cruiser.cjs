// Example policy: each capability owns its state; api/ is its declared public surface.
// Adapt paths to selected ownership; no layer names are required.
/** @type {import('dependency-cruiser').IConfiguration} */
module.exports = {
  forbidden: [
    {
      name: "no-circular",
      severity: "error",
      comment: "Constraint 1: module dependencies stay acyclic.",
      from: {},
      to: { circular: true },
    },
    {
      name: "no-cross-module-internals",
      severity: "error",
      comment:
        "Consumers use the declared api/ directory; owner-local imports stay legal.",
      // Module root: src/modules/<capability>. Adjust this regex to your layout.
      from: { path: "^src/modules/([^/]+)/" },
      to: {
        path: "^src/modules/[^/]+/(?!api/)",
        pathNot: "^src/modules/$1/",
      },
    },
    {
      name: "no-shared-to-modules",
      severity: "error",
      comment: "shared/ is infrastructure; it does not import business modules.",
      from: { path: "^src/shared/" },
      to: { path: "^src/modules/" },
    },
  ],
  options: {
    tsPreCompilationDeps: true,
    tsConfig: { fileName: "tsconfig.json" },
    doNotFollow: { path: "node_modules" },
    exclude: { path: "(^|/)(node_modules|dist|build|coverage)/" },
  },
};

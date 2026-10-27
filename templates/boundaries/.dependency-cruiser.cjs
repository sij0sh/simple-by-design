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
        "Constraint 2: import another module through api/ or its entry, not domain/ or persistence/.",
      // Module root: src/modules/<capability>. Adjust this regex to your layout.
      from: { path: "^src/modules/([^/]+)/" },
      to: {
        path: "^src/modules/[^/]+/(domain|persistence)/",
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
    doNotFollow: { path: "node_modules" },
    exclude: { path: "(^|/)(node_modules|dist|build|coverage)/" },
  },
};

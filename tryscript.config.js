export default {
  env: {
    NO_COLOR: "1",
    LC_ALL: "C",
  },
  path: ["$TRYSCRIPT_GIT_ROOT/.venv/bin"],
  patterns: {
    VERSION: "repren \\d+\\.\\d+\\.\\S+",
  },
  timeout: 15_000,
};

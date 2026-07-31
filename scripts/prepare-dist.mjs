import { cpSync, existsSync, mkdirSync, rmSync } from "node:fs";

if (!existsSync("out")) {
  throw new Error("Next.js export output was not found.");
}

rmSync("dist", { recursive: true, force: true });
mkdirSync("dist", { recursive: true });
cpSync("out", "dist", { recursive: true });
cpSync("public", "dist", { recursive: true });
mkdirSync("dist/server", { recursive: true });
mkdirSync("dist/.openai", { recursive: true });
cpSync("hosting/server/index.js", "dist/server/index.js");
cpSync(".openai/hosting.json", "dist/.openai/hosting.json");

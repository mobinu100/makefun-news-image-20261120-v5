import { copyFileSync, mkdirSync } from "node:fs";
import { join } from "node:path";

const out = process.env.MAKEFUN_OUTPUT_DIR ?? "out";
mkdirSync(out, { recursive: true });
copyFileSync(join(import.meta.dirname, "entry.png"), join(out, "entry.png"));

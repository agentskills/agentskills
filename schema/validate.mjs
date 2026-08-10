#!/usr/bin/env node

/**
 * Validates a SKILL.md frontmatter against the Agent Skills JSON Schema.
 *
 * Usage:
 *   node validate.mjs path/to/skill-name/SKILL.md
 *   node validate.mjs path/to/skill-name          # auto-finds SKILL.md
 *
 * Exit codes:
 *   0 — valid
 *   1 — validation errors
 *   2 — usage / file error
 */

import { readFileSync } from "node:fs";
import { existsSync, statSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { parseDocument } from "yaml";
import Ajv2020 from "ajv/dist/2020.js";

const __dirname = dirname(fileURLToPath(import.meta.url));

// ---------------------------------------------------------------------------
// Resolve SKILL.md path
// ---------------------------------------------------------------------------

let target = process.argv[2];

if (!target) {
  console.error("Usage: node validate.mjs <path/to/SKILL.md or skill-dir>");
  process.exit(2);
}

if (statSync(target, { throwIfNoEntry: false })?.isDirectory()) {
  const candidates = ["SKILL.md", "skill.md"];
  const found = candidates.find((c) => existsSync(join(target, c)));
  if (!found) {
    console.error(`Error: no SKILL.md found in ${target}`);
    process.exit(2);
  }
  target = join(target, found);
}

if (!existsSync(target)) {
  console.error(`Error: file not found: ${target}`);
  process.exit(2);
}

// ---------------------------------------------------------------------------
// Extract YAML frontmatter
// ---------------------------------------------------------------------------

const content = readFileSync(target, "utf-8");

if (!content.startsWith("---")) {
  console.error("Error: SKILL.md must start with YAML frontmatter (---)");
  process.exit(2);
}

const parts = content.split("---");
if (parts.length < 3) {
  console.error("Error: SKILL.md frontmatter not properly closed with ---");
  process.exit(2);
}

const frontmatterStr = parts[1];
const doc = parseDocument(frontmatterStr);

if (doc.errors.length > 0) {
  console.error("Error: invalid YAML in frontmatter:");
  doc.errors.forEach((e) => console.error(`  - ${e.message}`));
  process.exit(2);
}

const frontmatter = doc.toJSON();

// ---------------------------------------------------------------------------
// Validate against schema
// ---------------------------------------------------------------------------

const schema = JSON.parse(
  readFileSync(join(__dirname, "skill.schema.json"), "utf-8"),
);

const ajv = new Ajv2020({ allErrors: true });
const validate = ajv.compile(schema);
const valid = validate(frontmatter);

if (valid) {
  console.log(`✓ ${target}`);
} else {
  console.error(`✗ ${target}`);
  validate.errors.forEach((err) => {
    const path = err.instancePath || "(root)";
    console.error(`  - ${path}: ${err.message}`);
  });
  process.exit(1);
}

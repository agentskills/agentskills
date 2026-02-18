/**
 * Tests for the Agent Skills SKILL.md frontmatter JSON Schema.
 *
 * Validates that the schema correctly accepts valid frontmatter and rejects
 * invalid frontmatter, matching the constraints from the specification at
 * https://agentskills.io/specification
 *
 * Run:
 *   make test
 *   npm test
 *   node --test test_schema.mjs
 */

import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import Ajv2020 from "ajv/dist/2020.js";

const __dirname = dirname(fileURLToPath(import.meta.url));
const schema = JSON.parse(
  readFileSync(join(__dirname, "skill.schema.json"), "utf-8"),
);

const ajv = new Ajv2020({ allErrors: true });
const validate = ajv.compile(schema);

function assertValid(data, message) {
  const valid = validate(data);
  assert.ok(valid, message || `Expected valid but got errors: ${JSON.stringify(validate.errors)}`);
}

function assertInvalid(data, message) {
  const valid = validate(data);
  assert.ok(!valid, message || "Expected validation to fail");
}

// ---------------------------------------------------------------------------
// Valid frontmatter
// ---------------------------------------------------------------------------

describe("valid frontmatter", () => {
  it("accepts minimal frontmatter (name + description only)", () => {
    assertValid({ name: "my-skill", description: "A test skill" });
  });

  it("accepts all fields", () => {
    assertValid({
      name: "pdf-processing",
      description: "Extract text and tables from PDF files.",
      license: "Apache-2.0",
      compatibility: "Requires Python 3.11+",
      metadata: { author: "example-org", version: "1.0" },
      "allowed-tools": "Bash(git:*) Bash(jq:*) Read",
    });
  });

  it("accepts single-character name", () => {
    assertValid({ name: "a", description: "test" });
  });

  it("accepts name with digits", () => {
    assertValid({ name: "skill-2", description: "test" });
  });

  it("accepts name at max length (64 chars)", () => {
    assertValid({ name: "a".repeat(64), description: "test" });
  });

  it("accepts description at max length (1024 chars)", () => {
    assertValid({ name: "test", description: "x".repeat(1024) });
  });

  it("accepts compatibility at max length (500 chars)", () => {
    assertValid({
      name: "test",
      description: "test",
      compatibility: "x".repeat(500),
    });
  });

  it("accepts allowed-tools field", () => {
    assertValid({
      name: "test",
      description: "test",
      "allowed-tools": "Bash(jq:*) Bash(git:*)",
    });
  });
});

// ---------------------------------------------------------------------------
// Missing required fields
// ---------------------------------------------------------------------------

describe("required fields", () => {
  it("rejects missing name", () => {
    assertInvalid({ description: "test" });
  });

  it("rejects missing description", () => {
    assertInvalid({ name: "test" });
  });

  it("rejects empty object", () => {
    assertInvalid({});
  });
});

// ---------------------------------------------------------------------------
// Name validation
// ---------------------------------------------------------------------------

describe("name validation", () => {
  it("rejects uppercase letters", () => {
    assertInvalid({ name: "MySkill", description: "test" });
  });

  it("rejects leading hyphen", () => {
    assertInvalid({ name: "-my-skill", description: "test" });
  });

  it("rejects trailing hyphen", () => {
    assertInvalid({ name: "my-skill-", description: "test" });
  });

  it("rejects consecutive hyphens", () => {
    assertInvalid({ name: "my--skill", description: "test" });
  });

  it("rejects underscore", () => {
    assertInvalid({ name: "my_skill", description: "test" });
  });

  it("rejects spaces", () => {
    assertInvalid({ name: "my skill", description: "test" });
  });

  it("rejects name exceeding 64 chars", () => {
    assertInvalid({ name: "a".repeat(65), description: "test" });
  });

  it("rejects empty name", () => {
    assertInvalid({ name: "", description: "test" });
  });
});

// ---------------------------------------------------------------------------
// Description validation
// ---------------------------------------------------------------------------

describe("description validation", () => {
  it("rejects description exceeding 1024 chars", () => {
    assertInvalid({ name: "test", description: "x".repeat(1025) });
  });

  it("rejects empty description", () => {
    assertInvalid({ name: "test", description: "" });
  });
});

// ---------------------------------------------------------------------------
// Compatibility validation
// ---------------------------------------------------------------------------

describe("compatibility validation", () => {
  it("rejects compatibility exceeding 500 chars", () => {
    assertInvalid({
      name: "test",
      description: "test",
      compatibility: "x".repeat(501),
    });
  });

  it("rejects empty compatibility", () => {
    assertInvalid({ name: "test", description: "test", compatibility: "" });
  });
});

// ---------------------------------------------------------------------------
// Unknown fields
// ---------------------------------------------------------------------------

describe("unknown fields", () => {
  it("rejects fields not in the specification", () => {
    assertInvalid({
      name: "test",
      description: "test",
      unknown_field: "value",
    });
  });
});

// ---------------------------------------------------------------------------
// Metadata validation
// ---------------------------------------------------------------------------

describe("metadata validation", () => {
  it("rejects non-string metadata values", () => {
    assertInvalid({
      name: "test",
      description: "test",
      metadata: { count: 42 },
    });
  });
});

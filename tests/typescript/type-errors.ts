/**
 * Compile-Time Type Error Tests
 *
 * This file verifies that invalid compositions fail to compile.
 * Run with: npx tsc --noEmit tests/typescript/type-errors.ts
 *
 * Every @ts-expect-error comment MUST be followed by a compile error.
 * If the line compiles successfully, the test fails.
 */

import { Skill, SkillOutput, SkillOperation } from '../../src/types/skill';
import { compose, pipe } from '../../src/composition/compose';
import { skill, readSkill, writeSkill } from '../../src/types/builder';

// =============================================================================
// Test Skills with Incompatible Types
// =============================================================================

interface UserInput {
  userId: string;
}

interface UserOutput {
  user: {
    id: string;
    name: string;
    email: string;
  };
}

interface EmailInput {
  to: string;
  subject: string;
  body: string;
}

interface EmailOutput {
  sent: boolean;
  messageId: string;
}

// Create typed skills for testing
const fetchUser = readSkill<UserInput, UserOutput>({
  name: 'fetch-user',
  description: 'Fetches user by ID',
  fetch: async (input) => ({
    user: { id: input.userId, name: 'Test', email: 'test@example.com' },
  }),
  validateInput: (x): x is UserInput =>
    typeof x === 'object' && x !== null && typeof (x as UserInput).userId === 'string',
  validateOutput: (x): x is UserOutput =>
    typeof x === 'object' && x !== null && (x as UserOutput).user != null,
});

const sendEmail = writeSkill<EmailInput, EmailOutput>({
  name: 'send-email',
  description: 'Sends an email',
  write: async (_input) => ({ sent: true, messageId: 'msg-123' }),
  validateInput: (x): x is EmailInput =>
    typeof x === 'object' &&
    x !== null &&
    typeof (x as EmailInput).to === 'string' &&
    typeof (x as EmailInput).subject === 'string',
  validateOutput: (x): x is EmailOutput =>
    typeof x === 'object' && x !== null && typeof (x as EmailOutput).sent === 'boolean',
});

// =============================================================================
// COMPILE-TIME ERROR TESTS
// =============================================================================

// TEST 1: Incompatible output→input types should not compose
// fetchUser outputs { user: User }
// sendEmail expects { to: string, subject: string, body: string }
// These are completely incompatible

// @ts-expect-error - UserOutput is not assignable to EmailInput
const invalidComposition1 = compose(fetchUser, sendEmail);

// TEST 2: Reverse composition should also fail
// sendEmail outputs { sent: boolean, messageId: string }
// fetchUser expects { userId: string }

// @ts-expect-error - EmailOutput is not assignable to UserInput
const invalidComposition2 = compose(sendEmail, fetchUser);

// TEST 3: pipe() with incompatible chain should fail

// @ts-expect-error - Second skill input doesn't match first skill output
const invalidPipeline = pipe(fetchUser, sendEmail);

// =============================================================================
// Additional Type Mismatch Scenarios
// =============================================================================

interface NumberInput {
  value: number;
}

interface StringOutput {
  result: string;
}

interface ObjectInput {
  data: { nested: boolean };
}

const numberToString = readSkill<NumberInput, StringOutput>({
  name: 'number-to-string',
  description: 'Converts number to string',
  fetch: async (input) => ({ result: String(input.value) }),
  validateInput: (x): x is NumberInput =>
    typeof x === 'object' && x !== null && typeof (x as NumberInput).value === 'number',
  validateOutput: (x): x is StringOutput =>
    typeof x === 'object' && x !== null && typeof (x as StringOutput).result === 'string',
});

const processObject = readSkill<ObjectInput, StringOutput>({
  name: 'process-object',
  description: 'Processes object data',
  fetch: async (_input) => ({ result: 'processed' }),
  validateInput: (x): x is ObjectInput =>
    typeof x === 'object' && x !== null && (x as ObjectInput).data?.nested !== undefined,
  validateOutput: (x): x is StringOutput =>
    typeof x === 'object' && x !== null && typeof (x as StringOutput).result === 'string',
});

// TEST 4: String output cannot feed into object input

// @ts-expect-error - StringOutput is not assignable to ObjectInput
const invalidTypeChain = compose(numberToString, processObject);

// =============================================================================
// Missing Required Fields
// =============================================================================

interface FullInput {
  required1: string;
  required2: number;
  required3: boolean;
}

interface PartialOutput {
  required1: string;
  // Missing required2 and required3
}

const partialProducer = readSkill<{}, PartialOutput>({
  name: 'partial-producer',
  description: 'Produces partial output',
  fetch: async () => ({ required1: 'value' }),
  validateInput: (x): x is {} => true,
  validateOutput: (x): x is PartialOutput =>
    typeof x === 'object' && x !== null && typeof (x as PartialOutput).required1 === 'string',
});

const fullConsumer = readSkill<FullInput, {}>({
  name: 'full-consumer',
  description: 'Requires full input',
  fetch: async () => ({}),
  validateInput: (x): x is FullInput =>
    typeof x === 'object' &&
    x !== null &&
    typeof (x as FullInput).required1 === 'string' &&
    typeof (x as FullInput).required2 === 'number' &&
    typeof (x as FullInput).required3 === 'boolean',
  validateOutput: (x): x is {} => typeof x === 'object',
});

// TEST 5: Partial output cannot satisfy full input requirements

// @ts-expect-error - PartialOutput is missing required2 and required3
const missingFieldsComposition = compose(partialProducer, fullConsumer);

// =============================================================================
// VALID COMPOSITIONS (These should compile without errors)
// =============================================================================

interface TransformInput {
  user: { id: string; name: string; email: string };
}

interface TransformOutput {
  formatted: string;
}

const formatUser = readSkill<TransformInput, TransformOutput>({
  name: 'format-user',
  description: 'Formats user for display',
  fetch: async (input) => ({ formatted: `${input.user.name} <${input.user.email}>` }),
  validateInput: (x): x is TransformInput =>
    typeof x === 'object' && x !== null && (x as TransformInput).user != null,
  validateOutput: (x): x is TransformOutput =>
    typeof x === 'object' && x !== null && typeof (x as TransformOutput).formatted === 'string',
});

// This SHOULD compile - UserOutput matches TransformInput
const validComposition = compose(fetchUser, formatUser);

// Self-composition should work when types match
const selfComposable = readSkill<{ value: string }, { value: string }>({
  name: 'identity',
  description: 'Identity transform',
  fetch: async (input) => input,
  validateInput: (x): x is { value: string } =>
    typeof x === 'object' && x !== null && typeof (x as { value: string }).value === 'string',
  validateOutput: (x): x is { value: string } =>
    typeof x === 'object' && x !== null && typeof (x as { value: string }).value === 'string',
});

// This SHOULD compile - output type equals input type
const validSelfComposition = compose(selfComposable, selfComposable);

// =============================================================================
// Type Inference Verification
// =============================================================================

// Verify that composed skill has correct inferred types
async function testTypeInference() {
  // Input type should be UserInput
  const input: UserInput = { userId: '123' };

  // Output should be SkillOutput<TransformOutput>
  const result = await validComposition.execute(input);

  // This should work - result.data has formatted property
  const formatted: string = result.data.formatted;

  // @ts-expect-error - result.data does not have 'user' property
  const invalid: string = result.data.user;

  return { formatted, result };
}

console.log('Type error tests compiled successfully');
console.log('Run: npx tsc --noEmit tests/typescript/type-errors.ts');

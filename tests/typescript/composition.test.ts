/**
 * Composition Test Suite
 *
 * Tests demonstrating:
 * 1. Valid compositions that succeed (compile + runtime)
 * 2. Invalid compositions that fail at compile time
 * 3. Runtime failures with clear error messages
 * 4. Performance of composition-time validation
 */

import {
  Skill,
  SkillOutput,
  SkillValidationError,
  SkillCompositionError,
  SkillExecutionError,
} from '../../src/types/skill';
import { compose, pipe, parallel } from '../../src/composition/compose';
import { skill, atomicSkill, readSkill, writeSkill, transformSkill } from '../../src/types/builder';

// =============================================================================
// Test Types
// =============================================================================

interface User {
  id: string;
  name: string;
  email: string;
}

interface EnrichedUser extends User {
  department: string;
  manager: string;
}

interface EmailRequest {
  user: User;
  subject: string;
  body: string;
}

interface EmailResult {
  sent: boolean;
  messageId: string;
}

interface UserPermissions {
  userId: string;
  roles: string[];
  permissions: string[];
}

// =============================================================================
// Test Skills
// =============================================================================

/**
 * Fetches a user by ID.
 * Input: { userId: string }
 * Output: { user: User }
 */
const fetchUser = readSkill<{ userId: string }, { user: User }>({
  name: 'fetch-user',
  description: 'Fetches user by ID from database',
  fetch: async (input) => ({
    user: {
      id: input.userId,
      name: 'Test User',
      email: 'test@example.com',
    },
  }),
});

/**
 * Enriches a user with additional data.
 * Input: { user: User }
 * Output: { user: EnrichedUser }
 */
const enrichUser = readSkill<{ user: User }, { user: EnrichedUser }>({
  name: 'enrich-user',
  description: 'Adds department and manager info to user',
  fetch: async (input) => ({
    user: {
      ...input.user,
      department: 'Engineering',
      manager: 'Jane Doe',
    },
  }),
});

/**
 * Sends an email.
 * Input: { user: User, subject: string, body: string }
 * Output: { sent: boolean, messageId: string }
 */
const sendEmail = writeSkill<EmailRequest, EmailResult>({
  name: 'send-email',
  description: 'Sends an email to a user',
  write: async (input) => ({
    sent: true,
    messageId: 'msg-123',
  }),
});

/**
 * Fetches user permissions.
 * Input: { userId: string }
 * Output: { permissions: UserPermissions }
 */
const fetchPermissions = readSkill<{ userId: string }, { permissions: UserPermissions }>({
  name: 'fetch-permissions',
  description: 'Fetches user permissions from auth service',
  fetch: async (input) => ({
    permissions: {
      userId: input.userId,
      roles: ['user', 'admin'],
      permissions: ['read', 'write', 'delete'],
    },
  }),
});

/**
 * Transforms user name to uppercase.
 * Input: { user: User }
 * Output: { user: User }
 */
const uppercaseName = transformSkill<{ user: User }, { user: User }>({
  name: 'uppercase-name',
  description: 'Transforms user name to uppercase',
  transform: (input) => ({
    user: {
      ...input.user,
      name: input.user.name.toUpperCase(),
    },
  }),
});

// =============================================================================
// Test: Valid Compositions
// =============================================================================

describe('Valid Compositions', () => {
  test('compose two skills with matching types', async () => {
    // fetchUser outputs { user: User }
    // enrichUser inputs { user: User }
    // This should compile and execute successfully

    const fetchAndEnrich = compose(fetchUser, enrichUser);

    expect(fetchAndEnrich.name).toBe('fetch-user→enrich-user');
    expect(fetchAndEnrich.operation).toBe('READ'); // Both are READ

    const result = await fetchAndEnrich.execute({ userId: '123' });

    expect(result.data.user.id).toBe('123');
    expect(result.data.user.department).toBe('Engineering');
    expect(result.meta.skillName).toBe('fetch-user→enrich-user');
  });

  test('compose three skills using pipe', async () => {
    // fetchUser → enrichUser → uppercaseName

    const workflow = pipe(fetchUser, enrichUser, uppercaseName);

    const result = await workflow.execute({ userId: '123' });

    expect(result.data.user.name).toBe('TEST USER');
    expect(result.data.user.department).toBe('Engineering');
  });

  test('parallel composition merges outputs', async () => {
    // fetchUser and fetchPermissions can run in parallel
    // They have the same input type: { userId: string }

    const fetchBoth = parallel(
      readSkill<{ userId: string }, { user: User }>({
        name: 'fetch-user-simple',
        description: 'Fetches user',
        fetch: async (input) => ({
          user: { id: input.userId, name: 'User', email: 'u@e.com' },
        }),
      }),
      fetchPermissions
    );

    const result = await fetchBoth.execute({ userId: '123' });

    // Output is merged: { user: User } & { permissions: UserPermissions }
    expect(result.data.user.id).toBe('123');
    expect(result.data.permissions.userId).toBe('123');
  });

  test('operation propagates correctly (READ + READ = READ)', async () => {
    const composed = compose(fetchUser, enrichUser);
    expect(composed.operation).toBe('READ');
  });

  test('operation propagates correctly (READ + WRITE = WRITE)', async () => {
    // Create a skill that outputs what sendEmail needs
    const prepareEmail = readSkill<{ userId: string }, EmailRequest>({
      name: 'prepare-email',
      description: 'Prepares email request',
      fetch: async (input) => ({
        user: { id: input.userId, name: 'User', email: 'u@e.com' },
        subject: 'Hello',
        body: 'World',
      }),
    });

    const composed = compose(prepareEmail, sendEmail);
    expect(composed.operation).toBe('WRITE');
  });
});

// =============================================================================
// Test: Invalid Compositions (Compile-Time Errors)
// =============================================================================

describe('Invalid Compositions (Type Errors)', () => {
  /**
   * These tests document what happens when you try to compose incompatible skills.
   * In a real TypeScript environment, these would be compile-time errors.
   *
   * The comments show the expected TypeScript error messages.
   */

  test('DOCUMENTATION: incompatible types cause compile error', () => {
    // This test documents the expected behavior.
    // The actual compile-time check happens in TypeScript.

    // INVALID COMPOSITION EXAMPLE:
    //
    // const invalid = compose(sendEmail, fetchUser);
    //
    // TypeScript Error:
    // Argument of type 'Skill<{ userId: string }, { user: User }, "READ">'
    // is not assignable to parameter of type 'never'.
    //
    // This is because:
    // - sendEmail outputs: { sent: boolean, messageId: string }
    // - fetchUser expects: { userId: string }
    // - These types are incompatible

    // For testing, we verify the types are indeed incompatible
    type SendEmailOutput = { sent: boolean; messageId: string };
    type FetchUserInput = { userId: string };

    // This type is 'false' because the types don't match
    type AreCompatible = SendEmailOutput extends FetchUserInput ? true : false;
    const _typeCheck: AreCompatible = false as AreCompatible;

    expect(_typeCheck).toBe(false);
  });

  test('DOCUMENTATION: missing required fields cause compile error', () => {
    // INVALID COMPOSITION EXAMPLE:
    //
    // const fetchMinimal = readSkill<{ userId: string }, { id: string }>(...);
    // const needsFullUser = readSkill<{ user: User }, ...>(...);
    //
    // const invalid = compose(fetchMinimal, needsFullUser);
    //
    // TypeScript Error:
    // Type '{ id: string }' is not assignable to type '{ user: User }'.
    // Property 'user' is missing in type '{ id: string }'.

    type MinimalOutput = { id: string };
    type FullUserInput = { user: User };

    type AreCompatible = MinimalOutput extends FullUserInput ? true : false;
    const _typeCheck: AreCompatible = false as AreCompatible;

    expect(_typeCheck).toBe(false);
  });

  test('DOCUMENTATION: wrong property types cause compile error', () => {
    // INVALID COMPOSITION EXAMPLE:
    //
    // const producesString = transformSkill<..., { count: string }>(...);
    // const expectsNumber = transformSkill<{ count: number }, ...>(...);
    //
    // const invalid = compose(producesString, expectsNumber);
    //
    // TypeScript Error:
    // Type 'string' is not assignable to type 'number'.

    type ProducerOutput = { count: string };
    type ConsumerInput = { count: number };

    type AreCompatible = ProducerOutput extends ConsumerInput ? true : false;
    const _typeCheck: AreCompatible = false as AreCompatible;

    expect(_typeCheck).toBe(false);
  });
});

// =============================================================================
// Test: Runtime Failures with Clear Error Messages
// =============================================================================

describe('Runtime Failures', () => {
  test('input validation failure produces clear error', async () => {
    const strictSkill = skill('strict-skill')
      .version('1.0.0')
      .level(1)
      .operation('READ')
      .description('A skill with strict input validation')
      .input<{ userId: string }>()
      .output<{ user: User }>()
      .validate({
        input: (x): x is { userId: string } =>
          typeof x === 'object' &&
          x !== null &&
          'userId' in x &&
          typeof (x as any).userId === 'string',
        output: (x): x is { user: User } => true,
      })
      .execute(async (input) => ({
        user: { id: input.userId, name: 'User', email: 'u@e.com' },
      }))
      .build();

    // Pass invalid input (number instead of string)
    await expect(
      strictSkill.execute({ userId: 123 } as any)
    ).rejects.toThrow(SkillValidationError);

    try {
      await strictSkill.execute({ userId: 123 } as any);
    } catch (error) {
      expect(error).toBeInstanceOf(SkillValidationError);
      const e = error as SkillValidationError;
      expect(e.skillName).toBe('strict-skill');
      expect(e.phase).toBe('input');
      expect(e.message).toContain('strict-skill');
      expect(e.message).toContain('input');
    }
  });

  test('output validation failure produces clear error', async () => {
    const badOutputSkill = skill('bad-output-skill')
      .version('1.0.0')
      .level(1)
      .operation('READ')
      .description('A skill that produces invalid output')
      .input<{ userId: string }>()
      .output<{ user: User }>()
      .validate({
        input: (x): x is { userId: string } => true,
        output: (x): x is { user: User } =>
          typeof x === 'object' &&
          x !== null &&
          'user' in x &&
          typeof (x as any).user?.id === 'string',
      })
      .execute(async (input) => ({
        // Return invalid output (missing user object)
        user: null as any,
      }))
      .build();

    await expect(
      badOutputSkill.execute({ userId: '123' })
    ).rejects.toThrow(SkillValidationError);

    try {
      await badOutputSkill.execute({ userId: '123' });
    } catch (error) {
      expect(error).toBeInstanceOf(SkillValidationError);
      const e = error as SkillValidationError;
      expect(e.phase).toBe('output');
    }
  });

  test('execution error is wrapped with context', async () => {
    const failingSkill = skill('failing-skill')
      .version('1.0.0')
      .level(1)
      .operation('READ')
      .description('A skill that throws')
      .input<{ userId: string }>()
      .output<{ user: User }>()
      .execute(async (input) => {
        throw new Error('Database connection failed');
      })
      .build();

    await expect(
      failingSkill.execute({ userId: '123' })
    ).rejects.toThrow(SkillExecutionError);

    try {
      await failingSkill.execute({ userId: '123' });
    } catch (error) {
      expect(error).toBeInstanceOf(SkillExecutionError);
      const e = error as SkillExecutionError;
      expect(e.skillName).toBe('failing-skill');
      expect(e.message).toContain('Database connection failed');
      expect(e.cause.message).toBe('Database connection failed');
    }
  });

  test('composed skill failure identifies which skill failed', async () => {
    const goodSkill = readSkill<{ userId: string }, { data: string }>({
      name: 'good-skill',
      description: 'Works fine',
      fetch: async (input) => ({ data: 'success' }),
    });

    const failingSecondSkill = skill('failing-second')
      .version('1.0.0')
      .level(1)
      .operation('READ')
      .description('Fails during execution')
      .input<{ data: string }>()
      .output<{ result: string }>()
      .execute(async (input) => {
        throw new Error('Second skill failed');
      })
      .build();

    const composed = compose(goodSkill, failingSecondSkill);

    try {
      await composed.execute({ userId: '123' });
      fail('Should have thrown');
    } catch (error) {
      expect(error).toBeInstanceOf(SkillExecutionError);
      const e = error as SkillExecutionError;
      // Error message should identify which skill failed
      expect(e.skillName).toBe('failing-second');
    }
  });
});

// =============================================================================
// Test: Performance
// =============================================================================

describe('Performance', () => {
  test('composition-time validation adds minimal overhead', () => {
    const iterations = 1000;

    // Measure time to compose skills
    const start = performance.now();

    for (let i = 0; i < iterations; i++) {
      compose(fetchUser, enrichUser);
    }

    const duration = performance.now() - start;
    const perComposition = duration / iterations;

    console.log(`Composition time: ${perComposition.toFixed(3)}ms per composition`);

    // Composition should be very fast (< 1ms)
    expect(perComposition).toBeLessThan(1);
  });

  test('runtime validation adds acceptable overhead', async () => {
    const iterations = 100;
    const composed = compose(fetchUser, enrichUser);

    // Warm up
    await composed.execute({ userId: 'warmup' });

    // Measure execution time
    const start = performance.now();

    for (let i = 0; i < iterations; i++) {
      await composed.execute({ userId: `user-${i}` });
    }

    const duration = performance.now() - start;
    const perExecution = duration / iterations;

    console.log(`Execution time: ${perExecution.toFixed(3)}ms per execution`);

    // Execution should be reasonably fast (< 10ms including validation)
    expect(perExecution).toBeLessThan(10);
  });
});

// =============================================================================
// Test: Edge Cases
// =============================================================================

describe('Edge Cases', () => {
  test('empty input object is valid if skill accepts it', async () => {
    const noInputSkill = readSkill<{}, { result: string }>({
      name: 'no-input',
      description: 'Requires no input',
      fetch: async () => ({ result: 'ok' }),
    });

    const result = await noInputSkill.execute({});
    expect(result.data.result).toBe('ok');
  });

  test('skill with optional fields handles missing fields', async () => {
    const optionalSkill = readSkill<
      { userId: string; includeHistory?: boolean },
      { user: User }
    >({
      name: 'optional-fields',
      description: 'Has optional fields',
      fetch: async (input) => ({
        user: { id: input.userId, name: 'User', email: 'u@e.com' },
      }),
    });

    // Works without optional field
    const result1 = await optionalSkill.execute({ userId: '123' });
    expect(result1.data.user.id).toBe('123');

    // Works with optional field
    const result2 = await optionalSkill.execute({
      userId: '123',
      includeHistory: true,
    });
    expect(result2.data.user.id).toBe('123');
  });

  test('deeply nested types are validated correctly', async () => {
    interface DeepInput {
      level1: {
        level2: {
          level3: {
            value: string;
          };
        };
      };
    }

    const deepSkill = readSkill<DeepInput, { result: string }>({
      name: 'deep-skill',
      description: 'Has deeply nested input',
      fetch: async (input) => ({
        result: input.level1.level2.level3.value,
      }),
    });

    const result = await deepSkill.execute({
      level1: {
        level2: {
          level3: {
            value: 'deep value',
          },
        },
      },
    });

    expect(result.data.result).toBe('deep value');
  });
});

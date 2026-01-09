/**
 * Core Skill Type Definitions
 *
 * Type-safe skill composition. Invalid compositions fail at compile time.
 *
 * @example
 * ```typescript
 * const fetchUser: Skill<{ userId: string }, { user: User }> = ...;
 * const sendEmail: Skill<{ user: User }, { sent: boolean }> = ...;
 *
 * // This compiles
 * const workflow = compose(fetchUser, sendEmail);
 *
 * // This fails at compile time
 * const invalid = compose(sendEmail, fetchUser); // Error!
 * ```
 */

// =============================================================================
// Core Types
// =============================================================================

/** Operation classification for safety tracking */
export type SkillOperation = 'READ' | 'WRITE' | 'TRANSFORM';

/** Skill level in composition hierarchy */
export type SkillLevel = 1 | 2 | 3;

/**
 * Base skill interface.
 *
 * @typeParam TInput - Input type
 * @typeParam TOutput - Output type
 */
export interface Skill<TInput, TOutput> {
  readonly name: string;
  readonly version?: string;
  readonly level?: SkillLevel;
  readonly operation?: SkillOperation;
  readonly description?: string;

  execute(input: TInput): Promise<TOutput>;
}

// =============================================================================
// Type Utilities
// =============================================================================

/** Extract input type from a skill */
export type InputOf<S> = S extends Skill<infer I, any> ? I : never;

/** Extract output type from a skill */
export type OutputOf<S> = S extends Skill<any, infer O> ? O : never;

/**
 * Check if two skills can be composed.
 * True if output of S1 is assignable to input of S2.
 */
export type CanCompose<
  S1 extends Skill<any, any>,
  S2 extends Skill<any, any>
> = OutputOf<S1> extends InputOf<S2> ? true : false;

// =============================================================================
// Errors
// =============================================================================

/** Error when skill validation fails */
export class SkillValidationError extends Error {
  constructor(
    public readonly skillName: string,
    public readonly field: string,
    public readonly expected: string,
    public readonly received: string
  ) {
    super(
      `Validation failed in '${skillName}': ` +
      `expected ${expected} for ${field}, got ${received}`
    );
    this.name = 'SkillValidationError';
  }
}

/** Error when composition is invalid */
export class SkillCompositionError extends Error {
  constructor(
    public readonly producer: string,
    public readonly consumer: string,
    public readonly reason: string
  ) {
    super(`Cannot compose '${producer}' → '${consumer}': ${reason}`);
    this.name = 'SkillCompositionError';
  }
}

/** Error when execution fails */
export class SkillExecutionError extends Error {
  constructor(
    public readonly skillName: string,
    public readonly cause: Error
  ) {
    super(`Execution failed in '${skillName}': ${cause.message}`);
    this.name = 'SkillExecutionError';
    this.cause = cause;
  }
}

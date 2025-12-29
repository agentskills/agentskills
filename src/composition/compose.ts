/**
 * Type-Safe Skill Composition
 *
 * Compose skills in a type-safe manner. Invalid compositions fail at compile time.
 *
 * @example
 * ```typescript
 * // Valid - types match
 * const workflow = compose(fetchUser, sendEmail);
 *
 * // Invalid - compile error
 * const invalid = compose(sendEmail, fetchUser);
 * ```
 */

import {
  Skill,
  InputOf,
  OutputOf,
  CanCompose,
  SkillExecutionError,
} from '../types/skill';

// =============================================================================
// Composition Functions
// =============================================================================

/**
 * Compose two skills sequentially.
 *
 * Type-safe: only compiles if output of skill1 matches input of skill2.
 */
export function compose<A, B, C>(
  skill1: Skill<A, B>,
  skill2: CanCompose<Skill<A, B>, Skill<B, C>> extends true ? Skill<B, C> : never
): Skill<A, C> {
  const name = `${skill1.name}→${(skill2 as Skill<B, C>).name}`;
  const skill2Typed = skill2 as Skill<B, C>;

  return {
    name,
    async execute(input: A): Promise<C> {
      try {
        const intermediate = await skill1.execute(input);
        return await skill2Typed.execute(intermediate);
      } catch (error) {
        throw new SkillExecutionError(name, error as Error);
      }
    },
  };
}

/**
 * Compose multiple skills into a pipeline.
 */
export function pipe<A, B>(s1: Skill<A, B>): Skill<A, B>;
export function pipe<A, B, C>(
  s1: Skill<A, B>,
  s2: Skill<B, C>
): Skill<A, C>;
export function pipe<A, B, C, D>(
  s1: Skill<A, B>,
  s2: Skill<B, C>,
  s3: Skill<C, D>
): Skill<A, D>;
export function pipe<A, B, C, D, E>(
  s1: Skill<A, B>,
  s2: Skill<B, C>,
  s3: Skill<C, D>,
  s4: Skill<D, E>
): Skill<A, E>;
export function pipe(...skills: Skill<any, any>[]): Skill<any, any>;
export function pipe(...skills: Skill<any, any>[]): Skill<any, any> {
  if (skills.length === 0) {
    throw new Error('pipe requires at least one skill');
  }
  if (skills.length === 1) {
    return skills[0];
  }
  return skills.reduce((acc, skill) => composeAny(acc, skill));
}

/**
 * Execute skills in parallel with same input, merge outputs.
 */
export function parallel<TInput, O1, O2>(
  skill1: Skill<TInput, O1>,
  skill2: Skill<TInput, O2>
): Skill<TInput, O1 & O2> {
  const name = `parallel(${skill1.name}, ${skill2.name})`;

  return {
    name,
    async execute(input: TInput): Promise<O1 & O2> {
      const [r1, r2] = await Promise.all([
        skill1.execute(input),
        skill2.execute(input),
      ]);
      return { ...r1, ...r2 };
    },
  };
}

// =============================================================================
// Internal Helpers
// =============================================================================

/** Unchecked compose for pipe implementation */
function composeAny(
  skill1: Skill<any, any>,
  skill2: Skill<any, any>
): Skill<any, any> {
  return {
    name: `${skill1.name}→${skill2.name}`,
    async execute(input: any): Promise<any> {
      const intermediate = await skill1.execute(input);
      return await skill2.execute(intermediate);
    },
  };
}

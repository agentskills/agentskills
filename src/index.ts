/**
 * Composable Skills Framework
 *
 * Type-safe skill composition with compile-time validation.
 *
 * @example
 * ```typescript
 * import { Skill, compose } from 'agentskills';
 *
 * const fetchUser: Skill<{ userId: string }, { user: User }> = {
 *   name: 'fetch-user',
 *   async execute({ userId }) {
 *     return { user: await db.users.find(userId) };
 *   },
 * };
 *
 * const sendEmail: Skill<{ user: User }, { sent: boolean }> = {
 *   name: 'send-email',
 *   async execute({ user }) {
 *     await email.send(user.email, 'Welcome!');
 *     return { sent: true };
 *   },
 * };
 *
 * // Type-safe composition
 * const workflow = compose(fetchUser, sendEmail);
 * const result = await workflow.execute({ userId: '123' });
 * ```
 */

// Core types
export {
  Skill,
  SkillOperation,
  SkillLevel,
  InputOf,
  OutputOf,
  CanCompose,
  SkillValidationError,
  SkillCompositionError,
  SkillExecutionError,
} from './types/skill';

// Composition functions
export {
  compose,
  pipe,
  parallel,
} from './composition/compose';

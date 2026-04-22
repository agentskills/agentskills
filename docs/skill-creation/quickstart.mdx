---
title: "Quickstart"
description: "Create your first Agent Skill and see it work in VS Code."
---

In this tutorial, you'll create a skill that gives an agent the capability to roll dice using a random number generator.

## Prerequisites

- [VS Code](https://code.visualstudio.com/) with [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot)

<Note>
This tutorial uses VS Code, but Agent Skills are an open format. The same skill works in any compatible agent, including Claude Code and OpenAI Codex.
</Note>

## Create the skill

A skill is a folder containing a `SKILL.md` file. VS Code looks for skills in `.agents/skills/` by default. Create `.agents/skills/roll-dice/SKILL.md` in your project:

````markdown .agents/skills/roll-dice/SKILL.md
---
name: roll-dice
description: Roll dice using a random number generator. Use when asked to roll a die (d6, d20, etc.), roll dice, or generate a random dice roll.
---

To roll a die, use the following command that generates a random number from 1
to the given number of sides:

```bash
echo $((RANDOM % <sides> + 1))
```

```powershell
Get-Random -Minimum 1 -Maximum (<sides> + 1)
```

Replace `<sides>` with the number of sides on the die (e.g., 6 for a standard
die, 20 for a d20).
````

That's it — one file, under 20 lines. Here's what each part does:

- **`name`** — A short identifier for the skill. Must match the folder name.
- **`description`** — Tells the agent when to use this skill. This is how the agent decides whether to activate it.
- **The body** — Instructions the agent follows when the skill activates. Here, the agent is instructed to generate a random number using a terminal command, substituting the number of sides from the user's request.

## Try it out

1. Open your project in VS Code.
2. Open the Copilot Chat panel.
3. Select **Agent** mode from the mode dropdown at the bottom of the chat panel.
4. Type `/skills` to confirm that `roll-dice` appears in the list. If it doesn't, check that the file is at `.agents/skills/roll-dice/SKILL.md` relative to your project root.
5. Ask: **"Roll a d20"**

The agent should activate the `roll-dice` skill. It may ask for permission to run a terminal command — allow it. It will run the command and return a random number between 1 and 20.

<Note>
Tool-use reliability varies across models — some follow skill instructions and run commands consistently, while others may attempt to answer on their own. If the agent responds without running a terminal command, try selecting a different model from the model dropdown.
</Note>

## How it works

Here's what happened behind the scenes:

1. **Discovery** — When the chat session started, the agent scanned default skill directories and found your skill. It read only the `name` and `description`, just enough to know when the skill might be relevant.

2. **Activation** — When you asked about rolling dice, the agent matched your question to the skill's description and loaded the full `SKILL.md` body into context.

3. **Execution** — The agent followed the instructions in the body, adapting the terminal command to the number of sides in your request.

This process uses **progressive disclosure** to let the agent access many skills without loading all their instructions up front.

## Next steps

You've created a working Agent Skill. From here:

- **[Best practices](/skill-creation/best-practices)** — How to write skills that are well-scoped and effective.
- **[Optimizing skill descriptions](/skill-creation/optimizing-descriptions)** — Test and improve your skill's description so it activates on the right prompts.
- **[Specification](/specification)** — The complete format reference for `SKILL.md` files.
- **[Example skills](https://github.com/anthropics/skills)** — Browse real-world skills on GitHub.

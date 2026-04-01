{/*
  LogoCarousel component for the Agent Skills documentation.
  Shuffles logos on each page load for fair exposure.

  To add a new logo:
  1. Add logo files to /images/logos/[logo-name]/
  2. Add entry to the logos array below
*/}
export const LogoCarousel = () => {
  const logos = [
    {
      name: "Junie",
      description: "Junie is an LLM-agnostic coding agent built for real-world development. It is built on top of the IntelliJ Platform, so it understands your project the same way your editor does.",
      url: "https://junie.jetbrains.com/",
      lightSrc: "/images/logos/junie/junie-logo-on-white.svg",
      darkSrc: "/images/logos/junie/junie-logo-on-dark.svg",
      instructionsUrl: "https://junie.jetbrains.com/docs/agent-skills.html",
    },
    {
      name: "Gemini CLI",
      description: "An open-source AI agent that brings the power of Gemini directly into your terminal.",
      url: "https://geminicli.com",
      lightSrc: "/images/logos/gemini-cli/gemini-cli-logo_light.svg",
      darkSrc: "/images/logos/gemini-cli/gemini-cli-logo_dark.svg",
      instructionsUrl: "https://geminicli.com/docs/cli/skills/",
      sourceCodeUrl: "https://github.com/google-gemini/gemini-cli",
    },
    {
      name: "Autohand Code CLI",
      description: "Autohand Code CLI is an autonomous LLM-powered coding agent that lives in your terminal. It uses the ReAct (Reason + Act) pattern to understand your codebase, plan changes, and execute them with your approval.",
      url: "https://autohand.ai/",
      lightSrc: "/images/logos/autohand/autohand-light.svg",
      darkSrc: "/images/logos/autohand/autohand-dark.svg",
      scale: 0.8,
      instructionsUrl: "https://autohand.ai/docs/working-with-autohand-code/agent-skills.html",
      sourceCodeUrl: "https://github.com/autohandai/code-cli",
    },
    {
      name: "OpenCode",
      description: "OpenCode is an open source agent that helps you write code in your terminal, IDE, or desktop.",
      url: "https://opencode.ai/",
      lightSrc: "/images/logos/opencode/opencode-wordmark-light.svg",
      darkSrc: "/images/logos/opencode/opencode-wordmark-dark.svg",
      instructionsUrl: "https://opencode.ai/docs/skills/",
      sourceCodeUrl: "https://github.com/sst/opencode",
    },
    {
      name: "OpenHands",
      description: "OpenHands is the open platform for cloud coding agents. Scale from one to thousands of agents — open source, model-agnostic, and enterprise-ready.",
      url: "https://openhands.dev/",
      lightSrc: "/images/logos/openhands/openhands-logo-light.svg",
      darkSrc: "/images/logos/openhands/openhands-logo-dark.svg",
      instructionsUrl: "https://docs.openhands.dev/overview/skills",
      sourceCodeUrl: "https://github.com/OpenHands/OpenHands",
    },
    {
      name: "Mux",
      description: "Mux makes it easy to run parallel coding agents, each with its own isolated workspace, right from your browser or desktop. Mux is open source and LLM provider-agnostic.",
      url: "https://mux.coder.com/",
      lightSrc: "/images/logos/mux/mux-editor-light.svg",
      darkSrc: "/images/logos/mux/mux-editor-dark.svg",
      scale: 0.8,
      instructionsUrl: "https://mux.coder.com/agent-skills",
      sourceCodeUrl: "https://github.com/coder/mux",
    },
    {
      name: "Cursor",
      description: "Built to make you extraordinarily productive, Cursor is the best way to code with AI.",
      url: "https://cursor.com/",
      lightSrc: "/images/logos/cursor/LOCKUP_HORIZONTAL_2D_LIGHT.svg",
      darkSrc: "/images/logos/cursor/LOCKUP_HORIZONTAL_2D_DARK.svg",
      instructionsUrl: "https://cursor.com/docs/context/skills",
    },
    {
      name: "Amp",
      description: "Amp is the frontier coding agent that lets you wield the full power of leading models.",
      url: "https://ampcode.com/",
      lightSrc: "/images/logos/amp/amp-logo-light.svg",
      darkSrc: "/images/logos/amp/amp-logo-dark.svg",
      scale: 0.8,
      instructionsUrl: "https://ampcode.com/manual#agent-skills",
    },
    {
      name: "Letta",
      description: "Letta is the platform for building stateful agents: AI with advanced memory that can learn and self-improve over time.",
      url: "https://www.letta.com/",
      lightSrc: "/images/logos/letta/Letta-logo-RGB_OffBlackonTransparent.svg",
      darkSrc: "/images/logos/letta/Letta-logo-RGB_GreyonTransparent.svg",
      instructionsUrl: "https://docs.letta.com/letta-code/skills/",
      sourceCodeUrl: "https://github.com/letta-ai/letta",
    },
    {
      name: "Firebender",
      description: "Firebender is the first Android-native coding agent that writes features, tests them in the emulator, and fixes issues automatically.",
      url: "https://firebender.com/",
      lightSrc: "/images/logos/firebender/firebender-wordmark-light.svg",
      darkSrc: "/images/logos/firebender/firebender-wordmark-dark.svg",
      instructionsUrl: "https://docs.firebender.com/multi-agent/skills",
    },
    {
      name: "Goose",
      description: "An open source, extensible AI agent that goes beyond code suggestions — install, execute, edit, and test with any LLM.",
      url: "https://block.github.io/goose/",
      lightSrc: "/images/logos/goose/goose-logo-black.png",
      darkSrc: "/images/logos/goose/goose-logo-white.png",
      instructionsUrl: "https://block.github.io/goose/docs/guides/context-engineering/using-skills/",
      sourceCodeUrl: "https://github.com/block/goose",
    },
    {
      name: "GitHub",
      description: "GitHub Copilot works alongside you directly in your editor, suggesting whole lines or entire functions for you.",
      url: "https://github.com/",
      lightSrc: "/images/logos/github/GitHub_Lockup_Dark.svg",
      darkSrc: "/images/logos/github/GitHub_Lockup_Light.svg",
      instructionsUrl: "https://docs.github.com/en/copilot/concepts/agents/about-agent-skills",
      sourceCodeUrl: "https://github.com/microsoft/vscode-copilot-chat",
    },
    {
      name: "VS Code",
      description: "Visual Studio Code combines the simplicity of a code editor with what developers need for their core edit-build-debug cycle.",
      url: "https://code.visualstudio.com/",
      lightSrc: "/images/logos/vscode/vscode.svg",
      darkSrc: "/images/logos/vscode/vscode-alt.svg",
      instructionsUrl: "https://code.visualstudio.com/docs/copilot/customization/agent-skills",
      sourceCodeUrl: "https://github.com/microsoft/vscode",
    },
    {
      name: "Claude Code",
      description: "Claude Code is an agentic coding tool that reads your codebase, edits files, runs commands, and integrates with your development tools. Available in your terminal, IDE, desktop app, and browser.",
      url: "https://claude.ai/code",
      lightSrc: "/images/logos/claude-code/Claude-Code-logo-Slate.svg",
      darkSrc: "/images/logos/claude-code/Claude-Code-logo-Ivory.svg",
      instructionsUrl: "https://code.claude.com/docs/en/skills",
    },
    {
      name: "Claude",
      description: "Claude is Anthropic's AI, built for problem solvers. Tackle complex challenges, analyze data, write code, and think through your hardest work.",
      url: "https://claude.ai/",
      lightSrc: "/images/logos/claude-ai/Claude-logo-Slate.svg",
      darkSrc: "/images/logos/claude-ai/Claude-logo-Ivory.svg",
      instructionsUrl: "https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview",
    },
    {
      name: "OpenAI Codex",
      description: "Codex is OpenAI's coding agent for software development.",
      url: "https://developers.openai.com/codex",
      lightSrc: "/images/logos/oai-codex/OAI_Codex-Lockup_400px.svg",
      darkSrc: "/images/logos/oai-codex/OAI_Codex-Lockup_400px_Darkmode.svg",
      instructionsUrl: "https://developers.openai.com/codex/skills/",
      sourceCodeUrl: "https://github.com/openai/codex",
    },
    {
      name: "Piebald",
      description: "The ultimate agentic AI control experience for developers.",
      url: "https://piebald.ai",
      lightSrc: "/images/logos/piebald/Piebald_wordmark_light.svg",
      darkSrc: "/images/logos/piebald/Piebald_wordmark_dark.svg",
    },
    {
      name: "Factory",
      description: "Build faster with AI coding agents. Factory Droids automate coding, testing, and deployment for startups and enterprises.",
      url: "https://factory.ai/",
      lightSrc: "/images/logos/factory/factory-logo-light.svg",
      darkSrc: "/images/logos/factory/factory-logo-dark.svg",
      instructionsUrl: "https://docs.factory.ai/cli/configuration/skills.md",
    },
    {
      name: "pi",
      description: "Pi is a minimal terminal coding harness. Adapt pi to your workflows, not the other way around.",
      url: "https://shittycodingagent.ai/",
      lightSrc: "/images/logos/pi/pi-logo-light.svg",
      darkSrc: "/images/logos/pi/pi-logo-dark.svg",
      scale: 0.55,
      instructionsUrl: "https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/skills.md",
      sourceCodeUrl: "https://github.com/badlogic/pi-mono",
    },
    {
      name: "Databricks",
      description: "Genie Code is an autonomous AI partner purpose-built for data work in Databricks.",
      url: "https://databricks.com/",
      lightSrc: "/images/logos/databricks/databricks-logo-light.svg",
      darkSrc: "/images/logos/databricks/databricks-logo-dark.svg",
      instructionsUrl: "https://docs.databricks.com/aws/en/assistant/skills",
    },
    {
      name: "Agentman",
      description: "AI agents that run your entire medical practice back office with no EHR integration — eligibility, claims, prior authorization, denial recovery, inbox management, patient communications, Rx refills — so doctors and staff can focus on patients.",
      url: "https://agentman.ai/",
      lightSrc: "/images/logos/agentman/agentman-wordmark-light.svg",
      darkSrc: "/images/logos/agentman/agentman-wordmark-dark.svg",
      instructionsUrl: "https://agentman.ai/agentskills",
    },
    {
      name: "TRAE",
      description: "Trae is an adaptive AI IDE that transforms how you work, collaborating with you to run faster.",
      url: "https://trae.ai/",
      lightSrc: "/images/logos/trae/trae-logo-lightmode.svg",
      darkSrc: "/images/logos/trae/trae-logo-darkmode.svg",
      instructionsUrl: "https://www.trae.ai/blog/trae_tutorial_0115",
      sourceCodeUrl: "https://github.com/bytedance/trae-agent",
    },
    {
      name: "Spring AI",
      description: "The Spring AI project aims to streamline the development of applications that incorporate artificial intelligence functionality without unnecessary complexity.",
      url: "https://docs.spring.io/spring-ai/reference",
      lightSrc: "/images/logos/spring-ai/spring-ai-logo-light.svg",
      darkSrc: "/images/logos/spring-ai/spring-ai-logo-dark.svg",
      instructionsUrl: "https://spring.io/blog/2026/01/13/spring-ai-generic-agent-skills/",
      sourceCodeUrl: "https://github.com/spring-projects/spring-ai",
    },
    {
      name: "Roo Code",
      description: "Roo Code puts an entire AI dev team right in your editor, outpacing closed tools with deep project-wide context, multi-step agentic coding, and unmatched developer-centric flexibility.",
      url: "https://roocode.com",
      lightSrc: "/images/logos/roo-code/roo-code-logo-black.svg",
      darkSrc: "/images/logos/roo-code/roo-code-logo-white.svg",
      instructionsUrl: "https://docs.roocode.com/features/skills",
      sourceCodeUrl: "https://github.com/RooCodeInc/Roo-Code",
    },
    {
      name: "Mistral AI Vibe",
      description: "Mistral Vibe is a command-line coding assistant powered by Mistral's models. It provides a conversational interface to your codebase, allowing you to use natural language to explore, modify, and interact with your projects through a powerful set of tools.",
      url: "https://github.com/mistralai/mistral-vibe",
      lightSrc: "/images/logos/mistral-vibe/vibe-logo_black.svg",
      darkSrc: "/images/logos/mistral-vibe/vibe-logo_white.svg",
      scale: 0.55,
      instructionsUrl: "https://github.com/mistralai/mistral-vibe",
      sourceCodeUrl: "https://github.com/mistralai/mistral-vibe",
    },
    {
      name: "Command Code",
      description: "Command Code is a coding agent that continuously learns your coding taste. Our meta neuro-symbolic AI model taste-1 with continuous reinforcement learning combines LLMs with your coding taste.",
      url: "https://commandcode.ai/",
      lightSrc: "/images/logos/command-code/command-code-logo-for-light.svg",
      darkSrc: "/images/logos/command-code/command-code-logo-for-dark.svg",
      scale: 1.33,
      instructionsUrl: "https://commandcode.ai/docs/skills",
    },
    {
      name: "Ona",
      description: "Run a team of AI software engineers in the cloud. Orchestrated, governed, secured at the kernel.",
      url: "https://ona.com",
      lightSrc: "/images/logos/ona/ona-wordmark-light.svg",
      darkSrc: "/images/logos/ona/ona-wordmark-dark.svg",
      scale: 0.8,
      instructionsUrl: "https://ona.com/docs/ona/agents-md#skills-for-repository-specific-workflows",
    },
    {
      name: "VT Code",
      description: "VT Code is an open-source coding agent with LLM-native code understanding and robust shell safety. Supports multiple LLM providers with automatic failover and efficient context management.",
      url: "https://github.com/vinhnx/vtcode",
      lightSrc: "/images/logos/vtcode/vt_code_light.svg",
      darkSrc: "/images/logos/vtcode/vt_code_dark.svg",
      instructionsUrl: "https://github.com/vinhnx/vtcode/blob/main/docs/skills/SKILLS_GUIDE.md",
      sourceCodeUrl: "https://github.com/vinhnx/VTCode",
    },
    {
      name: "Qodo",
      description: "Qodo is an agentic code integrity platform for reviewing, testing, and writing code, integrating AI across development workflows to strengthen code quality at every stage.",
      url: "https://www.qodo.ai/",
      lightSrc: "/images/logos/qodo/qodo-logo-light.png",
      darkSrc: "/images/logos/qodo/qodo-logo-dark.svg",
      instructionsUrl: "https://www.qodo.ai/blog/how-i-use-qodos-agent-skills-to-auto-fix-issues-in-pull-requests/",
    },
    {
      name: "Laravel Boost",
      description: "Laravel Boost accelerates AI-assisted development by providing the essential guidelines and agent skills that help AI agents write high-quality Laravel applications that adhere to Laravel best practices.",
      url: "https://github.com/laravel/boost",
      lightSrc: "/images/logos/laravel-boost/boost-light-mode.svg",
      darkSrc: "/images/logos/laravel-boost/boost-dark-mode.svg",
      instructionsUrl: "https://laravel.com/docs/12.x/boost#agent-skills",
      sourceCodeUrl: "https://github.com/laravel/boost",
    },
    {
      name: "Emdash",
      description: "Emdash is a provider-agnostic desktop app that lets you run multiple coding agents in parallel, each isolated in its own git worktree, either locally or over SSH on a remote machine.",
      url: "https://emdash.sh",
      lightSrc: "/images/logos/emdash/emdash-logo-light.svg",
      darkSrc: "/images/logos/emdash/emdash-logo-dark.svg",
      instructionsUrl: "https://docs.emdash.sh/skills",
      sourceCodeUrl: "https://github.com/generalaction/emdash",
    },
    {
      name: "Snowflake",
      description: "Cortex Code is an AI-driven intelligent agent integrated into the Snowflake platform, optimized for complex data engineering, analytics, machine learning, and agent-building tasks.",
      url: "https://docs.snowflake.com/en/user-guide/cortex-code/cortex-code",
      lightSrc: "/images/logos/snowflake/snowflake-logo-light.svg",
      darkSrc: "/images/logos/snowflake/snowflake-logo-dark.svg",
      instructionsUrl: "https://docs.snowflake.com/en/user-guide/cortex-code/extensibility#extensibility-skills",
    },
    {
      name: "Kiro",
      description: "Kiro helps you do your best work by bringing structure to AI coding with spec-driven development.",
      url: "https://kiro.dev/",
      lightSrc: "/images/logos/kiro/kiro-logo-light.svg",
      darkSrc: "/images/logos/kiro/kiro-logo-dark.svg",
      instructionsUrl: "https://kiro.dev/docs/skills/",
    },
  ];

  /* Shuffle logos on component mount */
  const [shuffled, setShuffled] = useState(logos);

  useEffect(() => {
    const shuffle = (items) => {
      const copy = [...items];
      for (let i = copy.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [copy[i], copy[j]] = [copy[j], copy[i]];
      }
      return copy;
    };
    setShuffled(shuffle(logos));
  }, []);

  const row1 = shuffled.filter((_, i) => i % 2 === 0);
  const row2 = shuffled.filter((_, i) => i % 2 === 1);
  const row1Doubled = [...row1, ...row1];
  const row2Doubled = [...row2, ...row2];

  return (
    <>
      <div className="logo-carousel">
        <div className="logo-carousel-track" style={{ animation: 'logo-scroll 50s linear infinite' }}>
          {row1Doubled.map((logo, i) => (
            <div key={`${logo.name}-${i}`} style={{ width: 150 * (logo.scale || 1), maxWidth: "100%" }}>
              <a href={logo.url} className="block no-underline border-none w-full h-full">
                <img className="block dark:hidden object-contain w-full h-full" src={logo.lightSrc} alt={logo.name} noZoom />
                <img className="hidden dark:block object-contain w-full h-full" src={logo.darkSrc} alt={logo.name} noZoom />
              </a>
            </div>
          ))}
        </div>
      </div>
      <div className="logo-carousel">
        <div className="logo-carousel-track" style={{ animation: 'logo-scroll 60s linear infinite reverse' }}>
          {row2Doubled.map((logo, i) => (
            <div key={`${logo.name}-${i}`} style={{ width: 150 * (logo.scale || 1), maxWidth: "100%" }}>
              <a href={logo.url} className="block no-underline border-none w-full h-full">
                <img className="block dark:hidden object-contain w-full h-full" src={logo.lightSrc} alt={logo.name} noZoom />
                <img className="hidden dark:block object-contain w-full h-full" src={logo.darkSrc} alt={logo.name} noZoom />
              </a>
            </div>
          ))}
        </div>
      </div>
    </>
  );
};

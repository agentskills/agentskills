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
      url: "https://junie.jetbrains.com/",
      lightSrc: "/images/logos/junie/junie-logo-on-white.svg",
      darkSrc: "/images/logos/junie/junie-logo-on-dark.svg",
      instructionsUrl: "https://junie.jetbrains.com/docs/agent-skills.html",
    },
    {
      name: "Gemini CLI",
      url: "https://geminicli.com",
      lightSrc: "/images/logos/gemini-cli/gemini-cli-logo_light.svg",
      darkSrc: "/images/logos/gemini-cli/gemini-cli-logo_dark.svg",
      instructionsUrl: "https://geminicli.com/docs/cli/skills/",
      sourceCodeUrl: "https://github.com/google-gemini/gemini-cli",
    },
    {
      name: "Autohand Code CLI",
      url: "https://autohand.ai/",
      lightSrc: "/images/logos/autohand/autohand-light.svg",
      darkSrc: "/images/logos/autohand/autohand-dark.svg",
      width: "120px",
      instructionsUrl: "https://autohand.ai/docs/working-with-autohand-code/agent-skills.html",
      sourceCodeUrl: "https://github.com/autohandai/code-cli",
    },
    {
      name: "OpenCode",
      url: "https://opencode.ai/",
      lightSrc: "/images/logos/opencode/opencode-wordmark-light.svg",
      darkSrc: "/images/logos/opencode/opencode-wordmark-dark.svg",
      instructionsUrl: "https://opencode.ai/docs/skills/",
      sourceCodeUrl: "https://github.com/sst/opencode",
    },
    {
      name: "OpenHands",
      url: "https://www.all-hands.dev/",
      lightSrc: "/images/logos/openhands/openhands-logo-light.svg",
      darkSrc: "/images/logos/openhands/openhands-logo-dark.svg",
      instructionsUrl: "https://docs.openhands.dev/overview/skills",
      sourceCodeUrl: "https://github.com/OpenHands/OpenHands",
    },
    {
      name: "Mux",
      url: "https://mux.coder.com/",
      lightSrc: "/images/logos/mux/mux-editor-light.svg",
      darkSrc: "/images/logos/mux/mux-editor-dark.svg",
      width: "120px",
      instructionsUrl: "https://mux.coder.com/agent-skills",
      sourceCodeUrl: "https://github.com/coder/mux",
    },
    {
      name: "Cursor",
      url: "https://cursor.com/",
      lightSrc: "/images/logos/cursor/LOCKUP_HORIZONTAL_2D_LIGHT.svg",
      darkSrc: "/images/logos/cursor/LOCKUP_HORIZONTAL_2D_DARK.svg",
      instructionsUrl: "https://cursor.com/docs/context/skills",
    },
    {
      name: "Amp",
      url: "https://ampcode.com/",
      lightSrc: "/images/logos/amp/amp-logo-light.svg",
      darkSrc: "/images/logos/amp/amp-logo-dark.svg",
      width: "120px",
      instructionsUrl: "https://ampcode.com/manual#agent-skills",
    },
    {
      name: "Letta",
      url: "https://www.letta.com/",
      lightSrc: "/images/logos/letta/Letta-logo-RGB_OffBlackonTransparent.svg",
      darkSrc: "/images/logos/letta/Letta-logo-RGB_GreyonTransparent.svg",
      instructionsUrl: "https://docs.letta.com/letta-code/skills/",
      sourceCodeUrl: "https://github.com/letta-ai/letta",
    },
    {
      name: "Firebender",
      url: "https://firebender.com/",
      lightSrc: "/images/logos/firebender/firebender-wordmark-light.svg",
      darkSrc: "/images/logos/firebender/firebender-wordmark-dark.svg",
      instructionsUrl: "https://docs.firebender.com/multi-agent/skills",
    },
    {
      name: "Goose",
      url: "https://block.github.io/goose/",
      lightSrc: "/images/logos/goose/goose-logo-black.png",
      darkSrc: "/images/logos/goose/goose-logo-white.png",
      instructionsUrl: "https://block.github.io/goose/docs/guides/context-engineering/using-skills/",
      sourceCodeUrl: "https://github.com/block/goose",
    },
    {
      name: "GitHub",
      url: "https://github.com/",
      lightSrc: "/images/logos/github/GitHub_Lockup_Dark.svg",
      darkSrc: "/images/logos/github/GitHub_Lockup_Light.svg",
      instructionsUrl: "https://docs.github.com/en/copilot/concepts/agents/about-agent-skills",
      sourceCodeUrl: "https://github.com/microsoft/vscode-copilot-chat",
    },
    {
      name: "VS Code",
      url: "https://code.visualstudio.com/",
      lightSrc: "/images/logos/vscode/vscode.svg",
      darkSrc: "/images/logos/vscode/vscode-alt.svg",
      instructionsUrl: "https://code.visualstudio.com/docs/copilot/customization/agent-skills",
      sourceCodeUrl: "https://github.com/microsoft/vscode",
    },
    {
      name: "Claude Code",
      url: "https://claude.ai/code",
      lightSrc: "/images/logos/claude-code/Claude-Code-logo-Slate.svg",
      darkSrc: "/images/logos/claude-code/Claude-Code-logo-Ivory.svg",
      instructionsUrl: "https://code.claude.com/docs/en/skills",
    },
    {
      name: "Claude",
      url: "https://claude.ai/",
      lightSrc: "/images/logos/claude-ai/Claude-logo-Slate.svg",
      darkSrc: "/images/logos/claude-ai/Claude-logo-Ivory.svg",
      instructionsUrl: "https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview",
    },
    {
      name: "OpenAI Codex",
      url: "https://developers.openai.com/codex",
      lightSrc: "/images/logos/oai-codex/OAI_Codex-Lockup_400px.svg",
      darkSrc: "/images/logos/oai-codex/OAI_Codex-Lockup_400px_Darkmode.svg",
      instructionsUrl: "https://developers.openai.com/codex/skills/",
      sourceCodeUrl: "https://github.com/openai/codex",
    },
    {
      name: "Piebald",
      url: "https://piebald.ai",
      lightSrc: "/images/logos/piebald/Piebald_wordmark_light.svg",
      darkSrc: "/images/logos/piebald/Piebald_wordmark_dark.svg",
    },
    {
      name: "Factory",
      url: "https://factory.ai/",
      lightSrc: "/images/logos/factory/factory-logo-light.svg",
      darkSrc: "/images/logos/factory/factory-logo-dark.svg",
      instructionsUrl: "https://docs.factory.ai/cli/configuration/skills.md",
    },
    {
      name: "pi",
      url: "https://shittycodingagent.ai/",
      lightSrc: "/images/logos/pi/pi-logo-light.svg",
      darkSrc: "/images/logos/pi/pi-logo-dark.svg",
      width: "80px",
      instructionsUrl: "https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/skills.md",
      sourceCodeUrl: "https://github.com/badlogic/pi-mono",
    },
    {
      name: "Databricks",
      url: "https://databricks.com/",
      lightSrc: "/images/logos/databricks/databricks-logo-light.svg",
      darkSrc: "/images/logos/databricks/databricks-logo-dark.svg",
      instructionsUrl: "https://docs.databricks.com/aws/en/assistant/skills",
    },
    {
      name: "Agentman",
      url: "https://agentman.ai/",
      lightSrc: "/images/logos/agentman/agentman-wordmark-light.svg",
      darkSrc: "/images/logos/agentman/agentman-wordmark-dark.svg",
      instructionsUrl: "https://agentman.ai/agentskills",
    },
    {
      name: "TRAE",
      url: "https://trae.ai/",
      lightSrc: "/images/logos/trae/trae-logo-lightmode.svg",
      darkSrc: "/images/logos/trae/trae-logo-darkmode.svg",
      instructionsUrl: "https://www.trae.ai/blog/trae_tutorial_0115",
      sourceCodeUrl: "https://github.com/bytedance/trae-agent",
    },
    {
      name: "Spring AI",
      url: "https://docs.spring.io/spring-ai/reference",
      lightSrc: "/images/logos/spring-ai/spring-ai-logo-light.svg",
      darkSrc: "/images/logos/spring-ai/spring-ai-logo-dark.svg",
      instructionsUrl: "https://spring.io/blog/2026/01/13/spring-ai-generic-agent-skills/",
      sourceCodeUrl: "https://github.com/spring-projects/spring-ai",
    },
    {
      name: "Roo Code",
      url: "https://roocode.com",
      lightSrc: "/images/logos/roo-code/roo-code-logo-black.svg",
      darkSrc: "/images/logos/roo-code/roo-code-logo-white.svg",
      instructionsUrl: "https://docs.roocode.com/features/skills",
      sourceCodeUrl: "https://github.com/RooCodeInc/Roo-Code",
    },
    {
      name: "Mistral AI Vibe",
      url: "https://github.com/mistralai/mistral-vibe",
      lightSrc: "/images/logos/mistral-vibe/vibe-logo_black.svg",
      darkSrc: "/images/logos/mistral-vibe/vibe-logo_white.svg",
      width: "80px",
      instructionsUrl: "https://github.com/mistralai/mistral-vibe",
      sourceCodeUrl: "https://github.com/mistralai/mistral-vibe",
    },
    {
      name: "Command Code",
      url: "https://commandcode.ai/",
      lightSrc: "/images/logos/command-code/command-code-logo-for-light.svg",
      darkSrc: "/images/logos/command-code/command-code-logo-for-dark.svg",
      width: "200px",
      instructionsUrl: "https://commandcode.ai/docs/skills",
    },
    {
      name: "Ona",
      url: "https://ona.com",
      lightSrc: "/images/logos/ona/ona-wordmark-light.svg",
      darkSrc: "/images/logos/ona/ona-wordmark-dark.svg",
      width: "120px",
      instructionsUrl: "https://ona.com/docs/ona/agents-md#skills-for-repository-specific-workflows",
    },
    {
      name: "VT Code",
      url: "https://github.com/vinhnx/vtcode",
      lightSrc: "/images/logos/vtcode/vt_code_light.svg",
      darkSrc: "/images/logos/vtcode/vt_code_dark.svg",
      instructionsUrl: "https://github.com/vinhnx/vtcode/blob/main/docs/skills/SKILLS_GUIDE.md",
      sourceCodeUrl: "https://github.com/vinhnx/VTCode",
    },
    {
      name: "Qodo",
      url: "https://www.qodo.ai/",
      lightSrc: "/images/logos/qodo/qodo-logo-light.png",
      darkSrc: "/images/logos/qodo/qodo-logo-dark.svg",
      instructionsUrl: "https://www.qodo.ai/blog/how-i-use-qodos-agent-skills-to-auto-fix-issues-in-pull-requests/",
    },
    {
      name: "Laravel Boost",
      url: "https://github.com/laravel/boost",
      lightSrc: "/images/logos/laravel-boost/boost-light-mode.svg",
      darkSrc: "/images/logos/laravel-boost/boost-dark-mode.svg",
      instructionsUrl: "https://laravel.com/docs/12.x/boost#agent-skills",
      sourceCodeUrl: "https://github.com/laravel/boost",
    },
    {
      name: "Emdash",
      url: "https://emdash.sh",
      lightSrc: "/images/logos/emdash/emdash-logo-light.svg",
      darkSrc: "/images/logos/emdash/emdash-logo-dark.svg",
      instructionsUrl: "https://docs.emdash.sh/skills",
      sourceCodeUrl: "https://github.com/generalaction/emdash",
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
            <a key={`${logo.name}-${i}`} href={logo.url} style={{ textDecoration: 'none', border: 'none' }}>
              <img className="block dark:hidden object-contain" style={{ width: logo.width || '150px', maxWidth: '100%' }} src={logo.lightSrc} alt={logo.name} />
              <img className="hidden dark:block object-contain" style={{ width: logo.width || '150px', maxWidth: '100%' }} src={logo.darkSrc} alt={logo.name} />
            </a>
          ))}
        </div>
      </div>
      <div className="logo-carousel">
        <div className="logo-carousel-track" style={{ animation: 'logo-scroll 60s linear infinite reverse' }}>
          {row2Doubled.map((logo, i) => (
            <a key={`${logo.name}-${i}`} href={logo.url} style={{ textDecoration: 'none', border: 'none' }}>
              <img className="block dark:hidden object-contain" style={{ width: logo.width || '150px', maxWidth: '100%' }} src={logo.lightSrc} alt={logo.name} />
              <img className="hidden dark:block object-contain" style={{ width: logo.width || '150px', maxWidth: '100%' }} src={logo.darkSrc} alt={logo.name} />
            </a>
          ))}
        </div>
      </div>
    </>
  );
};

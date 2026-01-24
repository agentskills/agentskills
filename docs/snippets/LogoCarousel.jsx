{/*
  LogoCarousel component for the Agent Skills documentation.
  Shuffles logos on each page load for fair exposure.

  To add a new logo:
  1. Add logo files to /images/logos/[logo-name]/
  2. Add entry to the logos array below
*/}
export const LogoCarousel = () => {
  const logos = [
    { name: "Gemini CLI", url: "https://geminicli.com", lightSrc: "/images/logos/gemini-cli/gemini-cli-logo_light.svg", darkSrc: "/images/logos/gemini-cli/gemini-cli-logo_dark.svg" },
    { name: "Autohand Code CLI", url: "https://autohand.ai/", lightSrc: "/images/logos/autohand/autohand-light.svg", darkSrc: "/images/logos/autohand/autohand-dark.svg", width: "120px" },
    { name: "OpenCode", url: "https://opencode.ai/", lightSrc: "/images/logos/opencode/opencode-wordmark-light.svg", darkSrc: "/images/logos/opencode/opencode-wordmark-dark.svg" },
    { name: "Mux", url: "https://mux.coder.com/", lightSrc: "/images/logos/mux/mux-editor-light.svg", darkSrc: "/images/logos/mux/mux-editor-dark.svg", width: "120px" },
    { name: "Cursor", url: "https://cursor.com/", lightSrc: "/images/logos/cursor/LOCKUP_HORIZONTAL_2D_LIGHT.svg", darkSrc: "/images/logos/cursor/LOCKUP_HORIZONTAL_2D_DARK.svg" },
    { name: "Amp", url: "https://ampcode.com/", lightSrc: "/images/logos/amp/amp-logo-light.svg", darkSrc: "/images/logos/amp/amp-logo-dark.svg", width: "120px" },
    { name: "Letta", url: "https://www.letta.com/", lightSrc: "/images/logos/letta/Letta-logo-RGB_OffBlackonTransparent.svg", darkSrc: "/images/logos/letta/Letta-logo-RGB_GreyonTransparent.svg" },
    { name: "Firebender", url: "https://firebender.com/", lightSrc: "/images/logos/firebender/firebender-wordmark-light.svg", darkSrc: "/images/logos/firebender/firebender-wordmark-dark.svg" },
    { name: "Goose", url: "https://block.github.io/goose/", lightSrc: "/images/logos/goose/goose-logo-black.png", darkSrc: "/images/logos/goose/goose-logo-white.png" },
    { name: "GitHub", url: "https://github.com/", lightSrc: "/images/logos/github/GitHub_Lockup_Dark.svg", darkSrc: "/images/logos/github/GitHub_Lockup_Light.svg" },
    { name: "VS Code", url: "https://code.visualstudio.com/", lightSrc: "/images/logos/vscode/vscode.svg", darkSrc: "/images/logos/vscode/vscode-alt.svg" },
    { name: "Claude Code", url: "https://claude.ai/code", lightSrc: "/images/logos/claude-code/Claude-Code-logo-Slate.svg", darkSrc: "/images/logos/claude-code/Claude-Code-logo-Ivory.svg" },
    { name: "Claude", url: "https://claude.ai/", lightSrc: "/images/logos/claude-ai/Claude-logo-Slate.svg", darkSrc: "/images/logos/claude-ai/Claude-logo-Ivory.svg" },
    { name: "OpenAI Codex", url: "https://developers.openai.com/codex", lightSrc: "/images/logos/oai-codex/OAI_Codex-Lockup_400px.svg", darkSrc: "/images/logos/oai-codex/OAI_Codex-Lockup_400px_Darkmode.svg" },
    { name: "Piebald", url: "https://piebald.ai", lightSrc: "/images/logos/piebald/Piebald_wordmark_light.svg", darkSrc: "/images/logos/piebald/Piebald_wordmark_dark.svg" },
    { name: "Factory", url: "https://factory.ai/", lightSrc: "/images/logos/factory/factory-logo-light.svg", darkSrc: "/images/logos/factory/factory-logo-dark.svg" },
    { name: "pi", url: "https://shittycodingagent.ai/", lightSrc: "/images/logos/pi/pi-logo-light.svg", darkSrc: "/images/logos/pi/pi-logo-dark.svg", width: "80px" },
    { name: "Databricks", url: "https://databricks.com/", lightSrc: "/images/logos/databricks/databricks-logo-light.svg", darkSrc: "/images/logos/databricks/databricks-logo-dark.svg" },
    { name: "Agentman", url: "https://agentman.ai/", lightSrc: "/images/logos/agentman/agentman-wordmark-light.svg", darkSrc: "/images/logos/agentman/agentman-wordmark-dark.svg" },
    { name: "TRAE", url: "https://trae.ai/", lightSrc: "/images/logos/trae/trae-logo-lightmode.svg", darkSrc: "/images/logos/trae/trae-logo-darkmode.svg" },
    { name: "Spring AI", url: "https://docs.spring.io/spring-ai/reference", lightSrc: "/images/logos/spring-ai/spring-ai-logo-light.svg", darkSrc: "/images/logos/spring-ai/spring-ai-logo-dark.svg" },
    { name: "Roo Code", url: "https://roocode.com", lightSrc: "/images/logos/roo-code/roo-code-logo-black.svg", darkSrc: "/images/logos/roo-code/roo-code-logo-white.svg" },
    { name: "Mistral AI Vibe", url: "https://github.com/mistralai/mistral-vibe", lightSrc: "/images/logos/mistral-vibe/vibe-logo_black.svg", darkSrc: "/images/logos/mistral-vibe/vibe-logo_white.svg", width: "80px" },
    { name: "Command Code", url: "https://commandcode.ai/", lightSrc: "/images/logos/command-code/command-code-logo-for-light.svg", darkSrc: "/images/logos/command-code/command-code-logo-for-dark.svg", width: "200px" },
    { name: "Ona", url: "https://ona.com", lightSrc: "/images/logos/ona/ona-wordmark-light.svg", darkSrc: "/images/logos/ona/ona-wordmark-dark.svg", width: "120px" },
    { name: "VT Code", url: "https://github.com/vinhnx/vtcode", lightSrc: "/images/logos/vtcode/vtcode-logo-light.svg", darkSrc: "/images/logos/vtcode/vtcode-logo-dark.svg", width: "120px" },
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

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository. The project defines an open format for teaching AI agents specialized workflows through SKILL.md files.

## Documentation

The Agent Skills documentation site, defined in the `docs/` directory, is built with [Mintlify](https://mintlify.com). 

### Quick Start Commands

```bash
# Install Mintlify CLI (required for local development)
npm i -g mint

# Run local development server (run from /docs directory)
cd docs && mint dev

# Update Mintlify CLI if dev server issues occur
mint update
```

Local preview available at `http://localhost:3000`

### Development Notes

- **Navigation**: Defined in `docs/docs.json` under `navigation.pages` array
- **Adding pages**: Create new `.mdx` file in `/docs`, add filename (without extension) to navigation
- **Deployment**: Automatic on push to `main` branch
- **Troubleshooting**: If page shows 404, ensure you're running `mint dev` from directory containing `docs.json`

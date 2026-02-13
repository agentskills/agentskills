# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository. The project defines an open format for teaching AI agents specialized workflows through SKILL.md files.

## Documentation

The Agent Skills documentation site, defined in the `docs/` directory, is built with [Mintlify](https://mintlify.com). 

### Quick Start Commands

```bash
# Install dependencies (run from /docs directory)
cd docs && npm install

# Run local development server
npm run dev

# Update Mintlify CLI if dev server issues occur
npm run update
```

Local preview available at `http://localhost:3000`

### Development Notes

- **Navigation**: Defined in `docs/docs.json` under `navigation.pages` array
- **Adding pages**: Create new `.mdx` file in `/docs`, add filename (without extension) to navigation
- **Deployment**: Automatic on push to `main` branch
- **Troubleshooting**: If page shows 404, ensure you're running `mint dev` from directory containing `docs.json`

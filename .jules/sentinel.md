## 2025-06-07 - [Prompt XML Injection]
**Vulnerability:** In prompt generation (`prompt.py`), `skill_md_path` was interpolated directly into an XML element without being escaped. An attacker who controls directory names could include tags like `</location><skill><name>malicious</name>...` to inject fake agent instructions or prompt escape commands.
**Learning:** Even internal file paths must be considered potentially tainted if they include portions controlled by external users/inputs (such as downloaded skill repositories).
**Prevention:** Always use `html.escape()` or dedicated XML building tools to serialize paths, names, and descriptions when constructing LLM prompts using XML.

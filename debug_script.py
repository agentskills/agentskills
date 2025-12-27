from skills_ref.parser.extended_parser import ExtendedSkillParser
from skills_ref.validation.validator import SkillValidator
from pathlib import Path
import tempfile
import os

def debug_validator():
    with tempfile.TemporaryDirectory() as tmp_dir:
        d = Path(tmp_dir)
        (d / "SKILL.md").write_text("""---
name: debug
description: debug
---
[[MissingLink]]
""", encoding='utf-8')

        parser = ExtendedSkillParser(d)
        res = parser.parse()

        print("Nodes:", res.ast)
        print("Outbound Links:", res.index.outbound_links)
        print("Unresolved Links:", res.index.unresolved_links)

        validator = SkillValidator()
        validation_res = validator.validate(res.properties, res.ast, res.index, res.raw_body)

        print("Warnings:", validation_res.warnings)

if __name__ == "__main__":
    debug_validator()

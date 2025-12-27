import pytest
from skills_ref.parser.extended_parser import ExtendedSkillParser
from skills_ref.navigation.block_navigator import BlockNavigator, SkillRegistry
from skills_ref.integration.resolver import CrossSkillResolver
from skills_ref.integration.composition import SkillComposer, SkillComposition, CompositionStep, CompositionType

@pytest.fixture
def registry_with_skills(tmp_path):
    d1 = tmp_path / "skill1"
    d1.mkdir()
    (d1 / "SKILL.md").write_text("""---
name: skill1
description: Skill 1
---
# Section 1 ^s1
Content 1
""", encoding='utf-8')

    d2 = tmp_path / "skill2"
    d2.mkdir()
    (d2 / "SKILL.md").write_text("""---
name: skill2
description: Skill 2
---
# Section 2
Content 2
""", encoding='utf-8')

    reg = SkillRegistry()
    reg.register("skill1", ExtendedSkillParser(d1).parse())
    reg.register("skill2", ExtendedSkillParser(d2).parse())
    return reg

def test_resolver(registry_with_skills):
    resolver = CrossSkillResolver(registry_with_skills)

    # Resolve link to skill2
    ref = resolver.resolve("skill2", source_skill="skill1")
    assert ref
    assert ref.target_skill == "skill2"

    # Resolve link to skill1 block
    ref = resolver.resolve("skill1^s1", source_skill="skill2")
    assert ref
    assert ref.target_block == "s1"

    # Resolve link to non-existent
    ref = resolver.resolve("skill3", source_skill="skill1")
    assert ref is None

def test_composition_pipeline(registry_with_skills):
    navigator = BlockNavigator(registry_with_skills)
    composer = SkillComposer(registry_with_skills, navigator)

    comp = SkillComposition(
        name="pipeline1",
        description="Test Pipeline",
        composition_type=CompositionType.PIPELINE,
        steps=[
            CompositionStep(skill_name="skill1", section="section-1"),
            CompositionStep(skill_name="skill2", section="section-2")
        ]
    )

    result = composer.compose(comp)
    assert result.success
    assert len(result.steps) == 2
    assert "Content 1" in result.steps[0]['result'].content
    assert "Content 2" in result.steps[1]['result'].content

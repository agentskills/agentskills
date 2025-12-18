#!/bin/bash
# Validate agentskills in specified paths
# Usage: validate.sh <paths> <fail-on-error>

set -euo pipefail

PATHS="${1:-.}"
FAIL_ON_ERROR="${2:-true}"

# Initialize counters
AGENTSKILLS_FOUND=0
AGENTSKILLS_VALID=0
AGENTSKILLS_INVALID=0
ERRORS_JSON="[]"

# Find all SKILL.md files (case-insensitive)
find_skill_dirs() {
    local search_paths=($PATHS)
    local skill_dirs=()

    for path in "${search_paths[@]}"; do
        if [ -d "$path" ]; then
            # Find SKILL.md or skill.md files
            while IFS= read -r -d '' skill_md; do
                skill_dir=$(dirname "$skill_md")
                # Avoid duplicates
                if [[ ! " ${skill_dirs[*]} " =~ " ${skill_dir} " ]]; then
                    skill_dirs+=("$skill_dir")
                fi
            done < <(find "$path" -type f \( -name "SKILL.md" -o -name "skill.md" \) -print0 2>/dev/null)
        fi
    done

    printf '%s\n' "${skill_dirs[@]}"
}

# Parse validation errors and emit GitHub annotations
emit_annotations() {
    local skill_dir="$1"
    local errors="$2"
    local skill_md=""

    # Find the SKILL.md file path for annotations
    if [ -f "$skill_dir/SKILL.md" ]; then
        skill_md="$skill_dir/SKILL.md"
    elif [ -f "$skill_dir/skill.md" ]; then
        skill_md="$skill_dir/skill.md"
    fi

    # Emit each error as a GitHub annotation
    while IFS= read -r error; do
        if [ -n "$error" ]; then
            # Escape special characters for GitHub annotation
            escaped_error=$(echo "$error" | sed 's/%/%25/g; s/\r/%0D/g; s/\n/%0A/g')

            if [ -n "$skill_md" ]; then
                echo "::error file=$skill_md,line=1::$escaped_error"
            else
                echo "::error::[$skill_dir] $escaped_error"
            fi
        fi
    done <<< "$errors"
}

# Main validation loop
echo "Searching for agentskills in: $PATHS"
echo ""

mapfile -t SKILL_DIRS < <(find_skill_dirs)

if [ ${#SKILL_DIRS[@]} -eq 0 ]; then
    echo "No agentskills found in specified paths."
    {
        echo "agentskills-found=0"
        echo "agentskills-valid=0"
        echo "agentskills-invalid=0"
        echo "errors=[]"
    } >> "$GITHUB_OUTPUT"
    exit 0
fi

AGENTSKILLS_FOUND=${#SKILL_DIRS[@]}
echo "Found $AGENTSKILLS_FOUND agentskill(s)"
echo ""

for skill_dir in "${SKILL_DIRS[@]}"; do
    echo "Validating: $skill_dir"

    # Run validation
    if output=$(cd "$SKILLS_REF_PATH" && uv run skills-ref validate "$GITHUB_WORKSPACE/$skill_dir" 2>&1); then
        echo "  Valid"
        AGENTSKILLS_VALID=$((AGENTSKILLS_VALID + 1))
    else
        echo "  Invalid:"
        # Extract just the error messages (skip the "Validation failed for..." line)
        errors=$(echo "$output" | grep -E '^\s+-' | sed 's/^\s*-\s*//')

        if [ -n "$errors" ]; then
            while IFS= read -r error; do
                echo "    - $error"
            done <<< "$errors"

            # Emit GitHub annotations
            emit_annotations "$skill_dir" "$errors"

            # Add to JSON errors array
            skill_name=$(basename "$skill_dir")
            error_escaped=$(echo "$errors" | jq -Rs '.')
            ERRORS_JSON=$(echo "$ERRORS_JSON" | jq --arg dir "$skill_dir" --arg name "$skill_name" --argjson errs "$error_escaped" \
                '. + [{"directory": $dir, "name": $name, "errors": ($errs | split("\n") | map(select(. != "")))}]')
        fi

        AGENTSKILLS_INVALID=$((AGENTSKILLS_INVALID + 1))
    fi
    echo ""
done

# Summary
echo "========================================"
echo "Validation Summary"
echo "========================================"
echo "Agentskills found:   $AGENTSKILLS_FOUND"
echo "Valid:               $AGENTSKILLS_VALID"
echo "Invalid:             $AGENTSKILLS_INVALID"
echo ""

# Set outputs
{
    echo "agentskills-found=$AGENTSKILLS_FOUND"
    echo "agentskills-valid=$AGENTSKILLS_VALID"
    echo "agentskills-invalid=$AGENTSKILLS_INVALID"
    echo "errors<<EOF"
    echo "$ERRORS_JSON"
    echo "EOF"
} >> "$GITHUB_OUTPUT"

# Exit with error if requested and there are invalid skills
if [ "$FAIL_ON_ERROR" = "true" ] && [ "$AGENTSKILLS_INVALID" -gt 0 ]; then
    echo "::error::Validation failed: $AGENTSKILLS_INVALID agentskill(s) have errors"
    exit 1
fi

exit 0

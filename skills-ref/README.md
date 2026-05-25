# skills-ref

Agent Skills の参照ライブラリです。

> [!IMPORTANT]
> このライブラリはデモ目的です。本番利用は想定していません。

## インストール

### macOS / Linux

pip を使う場合:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

または [uv](https://docs.astral.sh/uv/) を使う場合:

```bash
uv sync
source .venv/bin/activate
```

### Windows

pip（PowerShell）を使う場合:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
```

pip（コマンドプロンプト）を使う場合:

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
pip install -e .
```

または [uv](https://docs.astral.sh/uv/) を使う場合:

```powershell
uv sync
.venv\Scripts\Activate.ps1
```

インストール後、`skills-ref` 実行ファイルは（有効化した仮想環境内の）`PATH` で利用可能になります。

## 使い方

### CLI

```bash
# スキルを検証
skills-ref validate path/to/skill

# スキルのプロパティを読む（JSON 出力）
skills-ref read-properties path/to/skill

# エージェントプロンプト用の <available_skills> XML を生成
skills-ref to-prompt path/to/skill-a path/to/skill-b
```

### Python API

```python
from pathlib import Path
from skills_ref import validate, read_properties, to_prompt

# スキルディレクトリを検証
problems = validate(Path("my-skill"))
if problems:
    print("検証エラー:", problems)

# スキルのプロパティを読む
props = read_properties(Path("my-skill"))
print(f"Skill: {props.name} - {props.description}")

# 利用可能スキル向けプロンプトを生成
prompt = to_prompt([Path("skill-a"), Path("skill-b")])
print(prompt)
```

## エージェントプロンプトへの統合

`to-prompt` を使うと、エージェントのシステムプロンプトに入れる推奨 `<available_skills>` XML ブロックを生成できます。この形式は Anthropic モデル向けの推奨ですが、Skill Client 側で利用モデルに応じて別形式にしても構いません。

```xml
<available_skills>
<skill>
<name>
my-skill
</name>
<description>
What this skill does and when to use it
</description>
<location>
/path/to/my-skill/SKILL.md
</location>
</skill>
</available_skills>
```

`<location>` 要素は、スキルの完全な手順がどこにあるかをエージェントに示します。

## ライセンス

Apache 2.0

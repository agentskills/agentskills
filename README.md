# Agent Skills

[![Discord](https://img.shields.io/badge/Discord-Join-5865F2?logo=discord&logoColor=white)](https://discord.gg/MKPE9g8aUy)

AIエージェントに新しい能力と専門性を与えるための、標準化された仕組みです。

## Agent Skillsとは？

Agent Skillsは、専門知識やワークフローを使ってAIエージェントの能力を拡張するための、軽量でオープンなフォーマットです。

スキルの中心は `SKILL.md` を含む1つのフォルダです。このファイルには最低限のメタデータ（`name` と `description`）と、特定のタスクをどう実行するかをエージェントに伝える手順が含まれます。スキルには、スクリプト、参照資料、テンプレート、その他のリソースも同梱できます。

```
my-skill/
├── SKILL.md          # 必須: メタデータ + 手順
├── scripts/          # 任意: 実行可能コード
├── references/       # 任意: ドキュメント
├── assets/           # 任意: テンプレート、リソース
└── ...               # 追加のファイル/ディレクトリ
```

## なぜAgent Skills？

エージェントの能力は高まっていますが、実務を安定してこなすための文脈が不足しがちです。Skillsは、手続き的知識や企業・チーム・ユーザー固有の文脈を、持ち運び可能でバージョン管理可能なフォルダとしてまとめ、必要時に読み込ませることでこの問題を解決します。これにより、エージェントは次を得られます。

- **ドメイン専門性**: 法務レビュー手順、データ分析パイプライン、プレゼン整形ルールなどの専門知識を、再利用可能な手順とリソースとして表現できます。
- **再現可能なワークフロー**: 複数ステップの作業を、一貫性があり監査可能な手順にできます。
- **製品横断での再利用**: 1度作成したスキルを、Skills対応の任意のエージェントで使い回せます。

## Agent Skillsの動作

エージェントは **段階的開示（progressive disclosure）** によって、3段階でスキルを読み込みます。

1. **Discovery（発見）**: 起動時に、利用可能な各スキルの名前と説明だけを読み込み、関連しそうかどうかだけを判断します。

2. **Activation（有効化）**: タスクがスキルの説明に合致したとき、`SKILL.md` の完全な手順をコンテキストに読み込みます。

3. **Execution（実行）**: 手順に従って実行し、必要に応じて同梱コードの実行や参照ファイルの読み込みを行います。

完全な手順は必要なときだけ読み込まれるため、コンテキスト消費を抑えつつ多くのスキルを保持できます。

## どこで使える？

Agent Skillsは、多くのAIツールやエージェントクライアントでサポートされています。詳しくは [Client Showcase](https://agentskills.io/clients) を参照してください。

## はじめ方

- **[Documentation](https://agentskills.io)** — ガイドとチュートリアル
- **[Specification](https://agentskills.io/specification)** — フォーマット仕様
- **[Example Skills](https://github.com/anthropics/skills)** — 実例
- **[Discord](https://discord.gg/MKPE9g8aUy)** — 作ったものの共有

## オープン開発

Agent Skillsフォーマットは [Anthropic](https://www.anthropic.com/) が最初に開発し、オープン標準として公開されました。現在は多くのエージェント製品に採用されています。この標準はエコシステム全体からのコントリビューションを歓迎しています。参加方法は [`CONTRIBUTING.md`](CONTRIBUTING.md) を参照してください。

## ライセンス

このリポジトリのコードは [Apache 2.0](LICENSE) でライセンスされています。ドキュメントは [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) です。詳細は各ディレクトリを参照してください。

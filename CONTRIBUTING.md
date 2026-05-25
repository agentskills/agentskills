# Agent Skills へのコントリビュート

Agent Skills への関心ありがとうございます。このドキュメントでは、コントリビュート方法と、フィードバックの投稿先を説明します。

## コントリビューションの種類

### ドキュメント改善

[ドキュメントサイト](https://agentskills.io) への改善提案を歓迎します。誤字修正、説明の明確化、より良い例、新しいガイド追加などが対象です。ドキュメントは `docs/` ディレクトリにあります。

### バグ報告

仕様、ドキュメント、参照ライブラリのバグを見つけた場合は、[Issue を作成](https://github.com/agentskills/agentskills/issues) してください。

### 提案・質問・フィードバック

機能要望、仕様設計の質問、一般的なフィードバックは [Discussion を開始](https://github.com/agentskills/agentskills/discussions) してください。提案やオープンな議論は Discussions、具体的な不具合は Issues と使い分けています。

提案は理論上の懸念ではなく、実際に遭遇した実装上の課題に基づくものにしてください。直面した問題と、提案がどう解決するかを示してください。

仕様への追加には高い基準を設けています。仕様は追加より削除のほうが難しいためです。新機能は実装者全員が理解・対応すべき複雑性を増やします。迷ったら、まず追加しない判断を優先してください。

> [!NOTE]
> **投稿先に迷う場合** はまず [Discussions](https://github.com/agentskills/agentskills/discussions) を利用してください。バグであればこちらで Issue に変換します。

### エコシステム掲載とロゴ申請

あなたの製品/プラットフォームが Agent Skills に対応している場合、[agentskills.io](https://agentskills.io) への掲載申請が可能です。製品は一般公開されており、現時点でスキルの検出・実行ができる必要があります。対応予定の発表のみ、またはクローズドベータ段階の製品は掲載しません。

以下を含む Pull Request を提出してください。

1. **ロゴファイル**: SVG 推奨、PNG も可（最小 200×200px）。ライト/ダーク両方を用意し、`docs/images/logos/` の既存形式に合わせてください。
2. **クライアントエントリ**: [`docs/snippets/clients.jsx`](docs/snippets/clients.jsx) の配列に製品を追加してください。
3. **製品情報**: PR 説明に、製品名、製品リンク、Skills 実装を示すドキュメントへのリンクを含めてください。

実装確認のため、デモやスクリーンショットの提出をお願いする場合があります。ロゴ申請は Anthropic チームがレビューします。

### 参照ライブラリ（`skills-ref/`）

参照ライブラリの方向性は現在検討中のため、現時点ではコードコントリビューションを受け付けていません。バグ報告は [Issues](https://github.com/agentskills/agentskills/issues)、フィードバックは [Discussions](https://github.com/agentskills/agentskills/discussions) で歓迎します。

### 現在受け付けていないもの

プロジェクト初期段階の焦点を保つため、現在は次を受け付けていません。

- **スキル投稿**: コミュニティスキルのディレクトリは現在運営していません（将来変更の可能性あり）。
- **大規模な設計変更**: コア仕様はまだ継続的に改善中であり、大規模な再設計は時期尚早です。

自分の提案が適切か迷う場合は、まず [Discussion](https://github.com/agentskills/agentskills/discussions) を作成してから大きな工数をかけてください。

## 開発セットアップ

### ドキュメントサイト

ドキュメントサイトは [Mintlify](https://mintlify.com/) で構築されています。

```bash
# Mintlify CLI をインストール
npm i -g mint

# docs/ ディレクトリからローカル開発サーバーを起動
cd docs && mint dev
```

ローカルプレビューは `http://localhost:3000` で確認できます。

## 変更の提出

1. [リポジトリを Fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo)
2. 変更用のブランチを作成
3. 変更を実施し、ローカルで動作確認
4. Pull Request を提出

PR は1つの論理的変更に絞り、関連 Issue があればリンクしてください。

## AI を使ったコントリビューション

> [!IMPORTANT]
> Agent Skills へコントリビュートする際に **何らかの AI 支援** を使った場合は、Pull Request または Issue で必ず開示してください。

Agent Skills の改善に AI ツールを活用することは歓迎されています。コード生成、問題検出、ドキュメント改善など、多くの有益なコントリビューションで AI が活用されています。

ただし、Claude Code や ChatGPT など、いかなる AI 支援を利用した場合でも、**Pull Request または Issue での開示が必須** です。また、AI をどの程度使ったか（例: 文書コメントのみか、コード生成も含むか）も記載してください。

PR の返信やコメントを AI が生成している場合も開示してください。

例外として、軽微なスペース修正や typo 修正は開示不要です。

開示例:

> This PR was written primarily by Claude Code.

より詳細な例:

> I consulted ChatGPT to understand the codebase but the solution was fully authored manually by myself.

AI 利用の未開示は、レビューする人間に対して不誠実であるだけでなく、どの程度の精査が必要かを判断しづらくします。

### 歓迎する提出内容

AI 支援ありのコントリビューションでは、次を満たしてください。

- **AI 利用の明確な開示**: 利用の有無と程度を明確にする
- **人間による理解**: 変更内容を本人が理解している
- **明確な根拠**: 変更の必要性と Agent Skills の目的への適合を説明できる
- **具体的な証拠**: 改善を示すテスト、シナリオ、例を含む

### クローズ対象

開示ポリシーに従っていないと判断される提出はクローズする場合があります。

## ライセンス

コントリビュートすることで、コードと仕様ファイルには [Apache License 2.0](LICENSE)、ドキュメントには [CC-BY 4.0](docs/LICENSE) が適用されることに同意したものとみなされます。

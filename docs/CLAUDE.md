# CLAUDE.md

このファイルは、Claude Code (claude.ai/code) がこのリポジトリで作業する際のガイダンスです。このプロジェクトは、SKILL.md ファイルを通じて AI エージェントに特化ワークフローを教えるためのオープンフォーマットを定義しています。

## ドキュメント

`docs/` ディレクトリで定義される Agent Skills ドキュメントサイトは、[Mintlify](https://mintlify.com) で構築されています。

### クイックスタートコマンド

```bash
# ローカル開発サーバーを起動
npm run dev
```

ローカルプレビュー: `http://localhost:3000`

### 開発メモ

- **ナビゲーション**: `docs/docs.json` の `navigation.pages` 配列で定義
- **ページ追加**: `/docs` に新しい `.mdx` ファイルを作成し、拡張子なしファイル名をナビゲーションに追加
- **デプロイ**: `main` ブランチへの push で自動実行
- **トラブルシュート**: ページが 404 の場合、`docs.json` を含むディレクトリで `mint dev` を実行しているか確認

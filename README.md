# Agent Skills 分享包

本資料夾收錄可直接安裝到 Claude Code、Codex 等 Agent 的 skill。

## 目前收錄

| Skill | 功能 | 出處 |
|---|---|---|
| grilling | 針對你的計畫、決策或想法「無情追問」，用設計樹（design tree）一輪一輪提問，直到沒有任何隱含假設為止。適合在動工前做壓力測試。 | [mattpocock/skills](https://github.com/mattpocock/skills)（MIT） |

## 安裝方式

### 方法一：skills.sh 安裝器（Claude Code、Codex 等皆可）

```bash
npx skills@latest add hsuyiping-rgb/agent-skills
```

執行後會列出本 repo 的 skill，勾選 `grilling` 並選擇要安裝到哪個 Agent 即可。

### 方法二：手動複製（Claude Code）

把 `skills/grilling/` 整個資料夾複製到：

- 專案層級：`<你的專案>/.claude/skills/grilling/`
- 全域層級：`~/.claude/skills/grilling/`

### 方法三：直接安裝原作者版本

```bash
npx skills@latest add mattpocock/skills
```

## 使用方式

安裝後在對話中說「grill 我這個計畫」「幫我壓力測試這個想法」，或直接輸入 `/grilling`，Agent 會開始一輪一輪提問，每題附上建議答案，等你回答後再推進下一輪。

## 授權

`grilling` 原作者為 Matt Pocock，以 MIT 授權釋出；本資料夾保留原始 LICENSE 檔。

### 一次安裝到 Claude Code、Codex、Antigravity

```bash
npx skills@latest add hsuyiping-rgb/agent-skills --skill grilling --agent claude-code,codex,antigravity
```

> 注意：ChatGPT 網頁版不支援 skills；GPT 使用者請在 Codex（CLI 或 IDE 擴充）上安裝。

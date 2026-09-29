---
name: agent-kit
description: AI Agent 環境設定懶人包（總入口）。一次檢查並串接 GitHub、NotebookLM、chezmoi 跨電腦同步、Obsidian（選用），並把「專案初始化／開工／收工」工作流程、Office 文件產生、grilling 追問等技能裝到 Claude Code、Codex（GPT）、Antigravity 三個平台。當使用者說「安裝懶人包」「環境設定」「一鍵設定」「全部安裝」「新電腦設定」「環境健檢」「連接 GitHub」「連接 NotebookLM」「設定 chezmoi」「跨電腦同步設定」「把技能裝到 Codex／Antigravity」時，請一定要使用此技能。日常的初始化、開工、收工請交給同套件的 project-init、startup、shutdown 技能。
---

# AI Agent 環境設定懶人包（agent-kit）

一個入口，把一台新電腦（或舊電腦健檢）帶到「可以跨電腦、跨 Agent 無縫接續工作」的狀態。

## 套件全貌

| 技能 | 觸發語 | 做什麼 |
|------|--------|--------|
| `agent-kit`（本技能） | 安裝懶人包、環境健檢 | 裝工具、串接服務、部署技能到三平台 |
| `project-init` | 初始化專案 | 建 `agents.md`＋`handoff.md` → GitHub 私有 repo → Obsidian 筆記 |
| `startup` | 開工、上次做到哪 | 讀交接檔、git status＋fetch，建議下一步 |
| `shutdown` | 收工、下班 | 改寫交接檔、commit＋push、寫 Obsidian、提醒 chezmoi |
| `office-docs` | 做成 Word／PPT／Excel | 產生 .docx／.pptx／.xlsx，中文字型不跑掉，轉圖檢查版面 |
| `grilling` | grill 我這個計畫 | 動工前一輪一輪追問，壓力測試計畫（Matt Pocock，MIT） |

`handoff.md` 是整套的核心：**收工寫、開工讀**，任何電腦、任何 Agent 都靠它接手。

## 核心原則

1. **先檢查、再動手**：每一步先偵測現況，已完成的標「✅ 已就緒」並跳過，不重裝、不覆蓋。
2. **登入交給本人**：`gh auth login`、`nlm login` 會開瀏覽器，由使用者本人完成；Agent 不代填帳號密碼、不讀取或回顯 token。
3. **改設定前先備份**：任何全域設定檔（MCP 設定、`config.toml`、`mcp_config.json`）修改前先複製成 `<檔名>.bak-<時間>`。
4. **不同步機密**：chezmoi 只管理 `skills/` 與規則檔，絕不加入 `~/.codex/config.toml`、`auth.json`、`~/.claude.json`、`.env` 等含金鑰的檔案。
5. **使用者確認才執行對外動作**：安裝軟體（winget/brew）、建立 GitHub repo、push dotfiles 前都先說明並等同意。
6. **優雅降級**：某步驟失敗或使用者跳過，記錄原因、繼續下一步，最後總表呈現。

## 步驟 0：辨識環境

- 作業系統：Windows 用 PowerShell（`$env:COMPUTERNAME`）；macOS／Linux 用 `hostname`。
- 目前是哪個 Agent：Claude Code、Codex 或 Antigravity（依自身身分判斷），回報時寫明。
- 偵測三平台是否存在（資料夾存在即視為已安裝）：

| 平台 | 全域技能資料夾 | MCP 設定位置 |
|------|---------------|-------------|
| Claude Code | `~/.claude/skills/` | `claude mcp add`（或 `~/.claude.json`） |
| Codex（GPT） | `~/.codex/skills/` | `~/.codex/config.toml` 的 `[mcp_servers.*]` |
| Antigravity | `~/.gemini/antigravity/skills/` | `~/.gemini/antigravity/mcp_config.json` |

先向使用者回報：「這台電腦偵測到：…；接下來要跑的步驟：…」，並問要全跑還是只跑部分。

## 步驟 1：基礎工具

檢查：`git --version`、`gh --version`、`node --version`、`uv --version`、`chezmoi --version`；要用 `office-docs` 轉圖檢查，另查 LibreOffice（`soffice --version`，選用）。缺的列出來，徵得同意後安裝：

| 工具 | Windows | macOS |
|------|---------|-------|
| Git | `winget install Git.Git` | `brew install git` |
| GitHub CLI | `winget install GitHub.cli` | `brew install gh` |
| Node.js | `winget install OpenJS.NodeJS.LTS` | `brew install node` |
| uv | `winget install astral-sh.uv` | `brew install uv` |
| chezmoi | `winget install twpayne.chezmoi` | `brew install chezmoi` |
| LibreOffice（選用） | `winget install TheDocumentFoundation.LibreOffice` | `brew install --cask libreoffice` |

Windows 注意：`python3` 可能被 Microsoft Store 別名攔截，Python 一律用 `py` 或 `uv run`。裝完新工具要開新終端機，PATH 才會生效。

## 步驟 2：GitHub

1. `gh auth status`：已登入 → 記下帳號（`gh api user --jq .login`），跳到 3。
2. 未登入 → 請使用者執行 `gh auth login --web --git-protocol https`，在瀏覽器完成授權。
3. 全域身分：`git config --global user.name`／`user.email` 沒設才問使用者要填什麼（不要自己編）。
4. 雲端硬碟（Google Drive）上的 repo：提醒之後在該 repo 內設 `git config windows.appendAtomically false`（Windows 專用）。

## 步驟 3：NotebookLM

1. `nlm --version`；沒有就 `uv tool install notebooklm-mcp-cli`。
2. `nlm doctor` 或 `nlm login --check`；未登入請使用者執行 `nlm login`（瀏覽器登入 Google）。
3. 註冊 MCP（只對步驟 0 偵測到的平台做）：
   - **Antigravity**：`nlm setup add antigravity`
   - **Claude Code**：有 `claude` 指令就 `nlm setup add claude-code`；只有桌面版時用 `claude mcp add --scope user notebooklm-mcp -- notebooklm-mcp`，兩者都不行就請使用者在設定介面手動加入 `notebooklm-mcp` 指令。
   - **Codex**：先備份 `~/.codex/config.toml`，若沒有 `[mcp_servers.notebooklm-mcp]` 區塊才在檔尾加上：
     ```toml
     [mcp_servers.notebooklm-mcp]
     command = "notebooklm-mcp"
     ```
     （Windows 若找不到指令，改填 `where notebooklm-mcp` 查到的完整路徑）
4. `nlm setup list` 確認狀態；提醒使用者**重開該 Agent** 後說「列出我的 NotebookLM 筆記本」驗證。
5. 登入過期時：`nlm login` 重新登入即可。

## 步驟 4：chezmoi 跨電腦同步

目標：技能改一次，所有電腦都拿得到。

1. `chezmoi source-path` 有結果 → 已初始化，跳到 3。
2. 未初始化：
   - 使用者已有 dotfiles repo → `chezmoi init --apply <GitHub帳號>`（預設 repo 名 `dotfiles`）。
   - 沒有 → 問是否建立**私有** repo：`chezmoi init` 後 `gh repo create <帳號>/dotfiles --private --source "$(chezmoi source-path)" --push`。
3. 把三平台的**技能資料夾**納管（只加存在的平台，且只加 `skills` 這一層）：
   ```
   chezmoi add ~/.claude/skills
   chezmoi add ~/.codex/skills
   chezmoi add ~/.gemini/antigravity/skills
   ```
   加之前先看資料夾內有沒有備份殘檔（如 `_backup`、`*.backup-*`），問使用者要不要排除（寫進 `.chezmoiignore`）。
4. **絕不加入**：`~/.codex/config.toml`、`~/.codex/auth.json`、`~/.claude.json`、`~/.gemini/settings.json`、任何 `.env`——這些含 token，只能各電腦手動設定。
5. `chezmoi diff` 給使用者看 → 同意後 `chezmoi cd` 內 `git add -A && git commit && git push`（commit 訊息用繁體中文）。
6. 日常用法寫進回報：
   - 改了技能 → `chezmoi re-add` → 到 source 目錄 commit＋push
   - 另一台電腦 → `chezmoi update`

## 步驟 5：Obsidian（選用，要 L3 筆記才需要）

1. 問使用者 vault 路徑（或搜尋含 `.obsidian` 子資料夾的目錄）。
2. `npm install -g @bitbonsai/mcpvault`。
3. 依平台註冊 MCP，指令為 `mcpvault <VAULT_PATH>`（或 `npx -y @bitbonsai/mcpvault <VAULT_PATH>`）：Claude 用 `claude mcp add --scope user obsidian -- npx -y @bitbonsai/mcpvault "<VAULT_PATH>"`；Codex 加 `[mcp_servers.obsidian]`；Antigravity 加進 `mcp_config.json` 的 `mcpServers`（先備份）。
4. 重開 Agent 後驗證能讀寫。

## 步驟 6：部署工作流程技能到三平台

本套件資料夾（含 `install.ps1`／`install.sh`）位置：本技能的上兩層（`<kit>/skills/agent-kit/` → `<kit>/`）。

- Windows：`powershell -ExecutionPolicy Bypass -File <kit>\install.ps1`（先加 `-DryRun` 預覽）
- macOS／Linux：`bash <kit>/install.sh --dry-run`，再正式執行

安裝腳本會：自動偵測平台 → 同名技能先備份到 `~/.agent-kit-backup/<時間>/` → 複製 `agent-kit`、`project-init`、`startup`、`shutdown`、`office-docs`、`grilling` 六個技能（可用 `-Skills` 只裝部分）。**已有同名技能時，先讓使用者看差異再決定是否覆蓋**（腳本預設會跳過已存在且內容不同的技能，加 `-Force`／`--force` 才覆蓋）。

## 步驟 7：回報總表

```
🧰 agent-kit 環境報告（<電腦名>，由 <Agent> 執行）
| 項目 | 狀態 | 說明 |
| 基礎工具 | ✅ | git 2.x／gh 2.x／node 22／uv 0.x／chezmoi 2.x |
| GitHub | ✅ | 已登入 <帳號> |
| NotebookLM | ⚠️ | 已登入；Codex 已註冊，Claude 需重開後驗證 |
| chezmoi | ✅ | 納管 3 個 skills 資料夾，已推 dotfiles |
| Obsidian | — | 使用者選擇跳過 |
| 技能部署 | ✅ | Claude／Codex／Antigravity 各 6 個 |
➡️ 待你手動：<例：重開 Codex、在另一台電腦跑 chezmoi update>
```

最後提醒：**重開每個 Agent**，新技能與 MCP 才會載入；接著到任一專案資料夾說「初始化專案」就能開始用。

## 不該做的事

- ❌ 代替使用者輸入密碼、token，或把 token 印在對話裡
- ❌ 把含金鑰的設定檔加進 chezmoi／git
- ❌ 沒備份就改 MCP 設定檔；沒問就覆蓋既有同名技能
- ❌ 沒徵得同意就安裝軟體、建 repo、push

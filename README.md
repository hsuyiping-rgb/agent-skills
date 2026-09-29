# Agent Skills 分享包

可同時安裝到 **Claude Code、Codex（GPT）、Antigravity** 的技能包：一次設定好環境，之後在任何電腦、用任何 Agent 都能接續工作，也能直接產出 Office 文件。

## 收錄技能

| 技能 | 說這句話就會啟動 | 做什麼 |
|------|-----------------|--------|
| `agent-kit` | 「安裝懶人包」「環境健檢」 | 檢查工具，串接 GitHub、NotebookLM、chezmoi、Obsidian（選用），把技能部署到三個平台 |
| `project-init` | 「初始化專案」 | 建 `agents.md`（專案藍圖）＋`handoff.md`（交接檔）→ GitHub 私有 repo → Obsidian 筆記 |
| `startup` | 「開工」「上次做到哪」 | 讀交接檔、git status＋fetch，提醒技能有新版，建議下一步 |
| `shutdown` | 「收工」「下班」 | 改寫 `handoff.md`、commit＋push、寫 Obsidian，提醒 chezmoi 同步 |
| `office-docs` | 「做成 Word／PPT／Excel」 | 產生 .docx／.pptx／.xlsx，中文字型不跑掉，轉圖目視檢查版面 |
| `grilling` | 「grill 我這個計畫」 | 動工前一輪一輪追問，直到沒有隱含假設（[mattpocock/skills](https://github.com/mattpocock/skills)，MIT） |

## 整套怎麼運作

```
初始化專案 ──► agents.md（藍圖）＋ handoff.md（交接檔）
                     │
   開工（讀） ◄──────┼──────► 收工（寫）
                     │
   GitHub：專案版本備份     chezmoi：技能跨電腦同步
   NotebookLM：資料研究     Obsidian：詳細工作筆記
```

`agents.md` 採跨 Agent 開放標準，三個平台都讀得懂：今天用 Claude 收工，明天在另一台電腦用 Codex 開工，也接得上。

## 安裝

### 方法零：最省事——把網址貼給 Agent

在 Claude Code、Codex 或 Antigravity 的對話框貼上：

```
https://github.com/hsuyiping-rgb/agent-skills
```

然後說「幫我下載這個 repo，執行 install 腳本安裝全部技能，再用 agent-kit 幫我設定環境」。中途跳出「是否允許執行指令」時按允許。

### 方法一：下載後執行安裝腳本（一次裝到三個平台）

```bash
git clone https://github.com/hsuyiping-rgb/agent-skills.git
cd agent-skills
```

Windows（先預覽、再安裝）：

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1 -DryRun
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

macOS／Linux：

```bash
bash install.sh --dry-run
bash install.sh
```

- 自動偵測電腦裝了哪些 Agent，只裝到存在的平台；也可指定：`-Targets codex,antigravity`、`-Skills office-docs,grilling`
- 已有同名但內容不同的技能會**跳過**；加 `-Force`（`--force`）才覆蓋，舊版備份到 `~/.agent-kit-backup/<時間>/`
- 裝完**重開每個 Agent**，再說「安裝懶人包」，讓 `agent-kit` 完成 GitHub、NotebookLM、chezmoi 串接

### 方法二：skills.sh 安裝器

需要 Node.js（`npx --version` 有版本號即可，沒有請到 <https://nodejs.org> 裝 LTS 版）：

```bash
npx skills@latest add hsuyiping-rgb/agent-skills --agent claude-code,codex,antigravity
```

只裝單一技能：加上 `--skill grilling`（或其他技能名稱）。

### 方法三：手動複製

把 `skills/<技能名>/` 整個資料夾複製到：

| 平台 | 全域技能資料夾 |
|------|---------------|
| Claude Code | `~/.claude/skills/` |
| Codex | `~/.codex/skills/` |
| Antigravity | `~/.gemini/antigravity/skills/` |

> ChatGPT 網頁版不支援 skills；GPT 使用者請在 Codex（CLI、App 或 IDE 擴充）上安裝。

## 需要的工具

| 工具 | 用途 | 必要性 |
|------|------|--------|
| Git、GitHub CLI（`gh`） | 專案版本備份 | 用到 GitHub 時 |
| uv | NotebookLM CLI、Office 文件腳本 | 建議 |
| chezmoi | 技能跨電腦同步 | 選用 |
| LibreOffice | Office 文件轉圖檢查 | 選用 |

不確定缺什麼？裝好技能後說「環境健檢」，`agent-kit` 會列出來並在你同意後代為安裝。

## 安全原則

- 登入（`gh auth login`、`nlm login`）一律由使用者本人在瀏覽器完成，Agent 不經手密碼與 token
- chezmoi 只同步 `skills/` 資料夾；`config.toml`、`auth.json`、`.claude.json`、`.env` 等含金鑰檔案**永不**納管
- 修改任何 MCP 設定檔前先備份；建立 GitHub repo 一律預設私有
- 安裝軟體、建 repo、push 前都會先徵得同意

## 授權

- `grilling`：原作者 Matt Pocock，MIT 授權，資料夾內保留原始 LICENSE
- 其餘技能：本 repo 作者自製，歡迎教育現場自由使用與修改

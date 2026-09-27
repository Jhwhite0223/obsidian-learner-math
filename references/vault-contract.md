# Vault contract

## 根目录与草稿

实际 Vault：`<ACTIVE_VAULT_ROOT>`。

Agent 只写 `01-收件箱/Agent草稿/`，可按主题使用：

- `设计文档/`
- `高等数学-同济八版上册/01-第一章 函数与极限/` 至 `07-第七章 微分方程/`
- 其他学科须先在 Agent草稿下建立不覆盖现有文件的子目录。

高数晚自习回答经用户明确“确认归档”后，统一移入既有 `20-知识/高等数学-同济八版上册/<对应章节>/晚自习问题汇总/`，保持与同类汇总连续编号和双链；归档前不要直接写入正式知识区。

附件统一放在 `附件/学习输入/YYYY/MM/`；原文件名需经安全 slug 处理且不得覆盖同名文件。

## 草稿元数据

每个 Markdown 草稿的 YAML 至少包含：

```yaml
agent_status: draft
source: <原文文件名、消息 ID 或双链>
created: <ISO-8601>
updated: <ISO-8601>
source_kind: chat|classroom|evening-study|example|question|image|pdf
course: <课程/学科>
topic: <主题>
content_hash: <UTF-8 内容 SHA-256>
```

高数必须核对“同济高等数学第八版上册”及章节；英语和智能采矿要检查课程名、题号/页码与术语。来源引用单独置于“原始来源/引用”，Agent 解释置于“Agent 解释”，不得混写或把待核实内容当事实。

## 数学公式存储与显示

Obsidian 使用 MathJax 渲染 LaTeX；公式源码必须以 UTF-8 保存。按以下层级输出：

- 短变量、关系和极限条件使用行内 `$...$`。
- 分式、积分、极限、多行等式使用独立 `$$...$$`；多行统一使用 `aligned`。
- 公式库草稿位置为 `01-收件箱/Agent草稿/高等数学-同济八版上册/高数公式库.md`。每个常用公式单独成块并添加短 ASCII 块 ID，例如 `^lim-sin`、`^ibp`。
- 其他笔记用 `![[高数公式库#^lim-sin]]` 嵌入，避免重复保存长 LaTeX 和解释。公式库确认后，才可移动到正式知识目录。
- 块引用必须使用 `#^`（不是 `^id`），否则 Obsidian 无法定位到指定块。
- 长公式不放在 Markdown 表格或窄 Callout 中；渲染失败时保留 LaTeX 源码，并给出一行纯文本 fallback，不改写原公式。
- UTF-8、分隔符和 LaTeX 源码可验证；不同主题、字体、设备宽度的像素级布局不作绝对承诺。

## 失败状态与停止条件

- `OCR_UNCERTAIN`：图片/PDF 无法清晰辨认；保留原件，标出模糊区域。
- `MISSING_CONDITION`：题目缺变量定义、单位、范围、页码或必要上下文。
- `SOURCE_CONFLICT`：Vault、用户文字与附件内容互相矛盾。
- `PATH_ESCAPE` / `DUPLICATE_TARGET`：目标越出 Vault 或附件/草稿同名；停止写入并报告路径。
- `WRITE_UNVERIFIED`：写入后无法重新读取、哈希不符或编码损坏；不得声称成功。

遇到任一状态，输出待用户确认的问题；不移动到正式目录。归档闸门是用户明确输入 **“确认归档”**，而不是 Agent 的推断。

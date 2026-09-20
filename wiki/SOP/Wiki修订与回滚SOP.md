# Wiki 修订与回滚 SOP

> 建立：2026-09-20 | 适用：`wiki/` 全部写操作 | 工具：`scripts/wiki_rev.py`
> 补的缺口：`wiki/` 早已在 git 里（Obsidian Git 自动提交），但改动大量淹没在批量
> `vault backup: <时间>` 提交中 —— **版本存在，回滚粒度不可用**。本 SOP 把已有 git
> 从「备份」升级为「可回滚的修订层」。

---

## 何时用（When）

| 场景 | 动作 |
|---|---|
| 要写**并发追加类高危文件**（见清单） | 写前 `guard` → 写后 `save` |
| 一次任务要**批量改多个文件** | 写前 `mark "<任务名>"` 建锚点 |
| 发现**刚写的内容是错的** | `rollback <file>` 预览 → `--yes` 回退 |
| 发现**上周写错了、现在才看出来** | `log <file>` 找该文件的语义提交 → `rollback <file> --to <sha>` |
| 要确认某文件近期**被谁改过** | `log <file>`（自动滤除 vault backup 噪音） |

**不适用**：新建文件、纯追加新章节（无覆盖风险）—— 不必 `mark`，直接写即可。

---

## 高危文件清单（并发追加类，必须 guard）

> 这些文件被多个 cron 任务反复写入，是最容易「锚点漂移 / 相互覆盖」的地方。

- `wiki/行业知识/结论索引.md`（8/17 舆情监控曾连续 3 次 edit 失败）
- `wiki/电影小镇/营销归因日志.md`（历史提交 **100% 埋在 vault backup 里**）
- `wiki/电影小镇/历史数据/index.md`
- `wiki/技术配置/GitHub高星标学习笔记.md`
- `MEMORY.md`

---

## 三条回滚路径

### 路径 1｜刚写坏，立即退（最常用）

```bash
python3 scripts/wiki_rev.py rollback wiki/路径/文件.md        # 只看 diff，不改动
python3 scripts/wiki_rev.py rollback wiki/路径/文件.md --yes  # 确认执行
```
恢复到该文件**上一次提交的版本**，丢弃未提交改动。原内容自动备份到
`/tmp/wiki_rev_backup/<时间戳>__<文件名>`，可反向撤回。

### 路径 2｜错误已在历史提交里

```bash
python3 scripts/wiki_rev.py log wiki/路径/文件.md      # 找到"上一次正确"的 sha
python3 scripts/wiki_rev.py rollback wiki/路径/文件.md --to <sha>        # 预览
python3 scripts/wiki_rev.py rollback wiki/路径/文件.md --to <sha> --yes  # 执行
```

### 路径 3｜只想定位到行，不想整文件退

```bash
git log -p -1 -- wiki/路径/文件.md     # 看最近一次改动全文
git blame wiki/路径/文件.md | sed -n '40,60p'   # 定位某行的提交
```

---

## 标准写流程（高危文件）

```bash
# ① 写前守卫：有没有别人的未提交改动会被我覆盖？
python3 scripts/wiki_rev.py guard wiki/路径/文件.md

# ② 写入（追加类用 cat >>，禁止 edit 锚点插入 —— 见 MEMORY 铁律）

# ③ 写后固化：给这次改动一个可检索的语义消息
python3 scripts/wiki_rev.py save "舆情监控 W39: 新增 3 条"
```

`save` 的意义在于让该文件的改动**可被单独定位** —— 否则它会被下一次
`vault backup` 吞掉，事后无法回答「这条结论是哪次任务写进去的」。

---

## 硬性安全约束

1. `rollback` **默认只预览**，必须显式 `--yes` 才改文件
2. **只回滚指定文件** —— 工具内不存在 `git reset --hard` / `git clean`
3. 回滚前**自动备份**原内容到 `/tmp/wiki_rev_backup/`
4. 批量改动**先 `mark` 锚点**，再动手；锚点是「回退到此处」的语义坐标
5. 已推送的提交**不要改写历史**（无 `--force`）；需要撤销就用 `rollback --to`

---

## 与既有规则的关系

- 衔接 `wiki/schema/rules.md` R1-R7（结构迁移必须同步引用它的脚本）
- 衔接 MEMORY 铁律「结论索引.md 用 `cat >>` 追加，禁止 edit 锚点插入」
- **不替代** quality_gate（那是"生成得对不对"的裁决，本 SOP 是"改坏了能不能退"的恢复）

---

*建立 2026-09-20 · 工具 `scripts/wiki_rev.py`（自测通过：预览/确认/回滚/校验四步）*

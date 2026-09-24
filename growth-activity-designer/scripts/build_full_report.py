#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成「方案报告（含实验判读）」——在 S8 评审报告基础上追加 11-实验判读与定档。

为何独立成脚本（而不并入 render_report.py）：
  skill 的产出边界是"可评审的产品方案"（见 SKILL.md），S1-S8 到 07-产品方案.md 为止。
  本脚本产出的是**上线后**的完整交付物（设计 → 实验 → 定档闭环），属于 run 目录的
  后置记录，不参与台账流程。把它与 S8 渲染器分开，边界才不会被混淆。

用法：
  python3 build_full_report.py <run_dir>
校验：
  关键区块齐全 → exit 0；否则 exit 1。
"""
import html, os, re, sys

for _s in (sys.stdout, sys.stderr):
    if _s is not None:
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

BASE = "10-方案可视化.html"
EXTRA = "11-实验判读与定档.md"
OUTPUT = "11-方案报告（含实验判读）.html"


def md2html(md):
    """极简 markdown → html，与 render_report.py 同源，只做标签转换、不改内容。"""
    out, table, ul = [], [], False

    def inline(s):
        s = html.escape(s)
        s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
        s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
        return s

    def flush_table():
        nonlocal table
        if not table:
            return
        rows = [r for r in table if not re.match(r"^\|[\s:\-|]+\|$", r)]
        h = ["<table>"]
        for i, r in enumerate(rows):
            cells = [c.strip() for c in r.strip().strip("|").split("|")]
            tag = "th" if i == 0 else "td"
            h.append("<tr>" + "".join(f"<{tag}>{inline(c)}</{tag}>" for c in cells) + "</tr>")
        h.append("</table>")
        out.append("\n".join(h))
        table = []

    for line in md.splitlines():
        if line.strip().startswith("|"):
            table.append(line)
            continue
        flush_table()
        if line.startswith(">"):
            out.append(f"<blockquote>{inline(line.lstrip('> '))}</blockquote>")
        elif line.startswith("#"):
            lvl = min(len(line) - len(line.lstrip("#")), 4)
            out.append(f"<h{lvl+1}>{inline(line.lstrip('# '))}</h{lvl+1}>")
        elif line.strip().startswith(("- ", "* ")):
            if not ul:
                out.append("<ul>")
                ul = True
            out.append(f"<li>{inline(line.strip()[2:])}</li>")
        else:
            if ul:
                out.append("</ul>")
                ul = False
            if line.strip():
                out.append(f"<p>{inline(line)}</p>")
    if ul:
        out.append("</ul>")
    flush_table()
    return "\n".join(out)


def extract_table(md, after_kw):
    """取某关键词之后出现的第一张表。"""
    seen, rows = False, []
    for line in md.splitlines():
        if after_kw in line:
            seen = True
        if seen and line.strip().startswith("|"):
            rows.append(line)
        elif seen and rows:
            break
    return md2html("\n".join(rows)) if rows else ""


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    rd = sys.argv[1]
    src = os.path.join(rd, BASE)
    md_path = os.path.join(rd, EXTRA)
    for p, name in ((src, BASE), (md_path, EXTRA)):
        if not os.path.exists(p):
            print(f"❌ 缺少输入文件：{name}")
            sys.exit(1)

    page = open(src, encoding="utf-8").read()
    md11 = open(md_path, encoding="utf-8").read()

    # 1) 顶部补一个徽章，标明本版已含上线后判读
    page = page.replace(
        "<span class='badge'>评审版</span>",
        "<span class='badge'>评审版</span>"
        "<span class='badge' style='background:#fff;color:#e2231a'>已含上线后实验判读</span>",
        1,
    )

    # 2) 一页纸追加「判读结果（上线后）」卡片
    card_anchor = "</div>\n <div class='card'><h2>关键决策点（请示项）</h2>"
    new_card = "\n  <div class='card'><h2>判读结果（上线后）</h2>" + extract_table(md11, "判读结果") + "</div>"
    if card_anchor in page:
        page = page.replace(card_anchor, new_card + "\n</div>\n <div class='card'><h2>关键决策点（请示项）</h2>", 1)

    # 3) 完整方案末尾追加折页区块（默认展开）
    tail = "</table></div></details>\n</div></body></html>"
    block = ("<details open><summary>上线后 · 实验判读与定档</summary>"
             "<div class='card'>" + md2html(md11) + "</div></details>")
    if tail in page:
        page = page.replace(tail, "</table></div></details>\n" + block + "\n</div></body></html>", 1)

    # 4) 一页纸标题上方加一行来源说明
    h2 = "<h2 style='margin:18px 4px'>一页纸 · 评审要点</h2>"
    note = ("<blockquote>本版在 S1–S7 评审报告基础上，追加了 <code>" + EXTRA + "</code>"
            "（上线后复盘记录，非 skill 产物）——见文末「上线后 · 实验判读与定档」。</blockquote>" + h2)
    if h2 in page:
        page = page.replace(h2, note, 1)

    out_path = os.path.join(rd, OUTPUT)
    open(out_path, "w", encoding="utf-8").write(page)

    checks = {
        "判读结果卡片": "判读结果（上线后）" in page,
        "判读折页区块": "上线后 · 实验判读与定档</summary>" in page,
        "来源说明": EXTRA in page,
        "顶部徽章": "已含上线后实验判读" in page,
        "HTML 收尾完整": page.rstrip().endswith("</html>"),
    }
    bad = [k for k, v in checks.items() if not v]
    if bad:
        print(f"❌ 关键区块缺失：{bad}")
        sys.exit(1)
    print(f"✅ 生成成功：{out_path}（{os.path.getsize(out_path)/1024:.1f} KB，区块 {len(checks)} 项齐全）")


if __name__ == "__main__":
    main()

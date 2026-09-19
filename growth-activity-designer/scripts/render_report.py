#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
S8 方案可视化：读 runs 产物（S1-S7 全部 md）+ ledger，按固化模板机械渲染 HTML 方案报告。
代码管渲染，不改写任何内容；改方案重跑即重渲染。
用法：python3 render_report.py <run_dir>
门禁语义：渲染成功且关键区块齐全 → exit 0；否则 exit 1。
"""
import html, json, os, re, sys

# 中文 Windows（GBK 控制台）兼容：强制 UTF-8 输出，避免 emoji/中文打印崩溃（UnicodeEncodeError）
for _s in (sys.stdout, sys.stderr):
    if _s is not None:
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            try:
                _s.reconfigure(errors="replace")
            except Exception:
                pass

FILES = [("01-活动画像.md", "S1 活动画像"), ("02-信息底座.md", "S2 信息底座"),
         ("03-活动规则.md", "S3 活动规则"), ("04-逆向方案.md", "S4 逆向与风控"),
         ("05-曝光动线.md", "S5 曝光动线"), ("06-成本与实验.md", "S6 成本与实验"),
         ("07-产品方案.md", "S7 方案汇编"), ("08-决策点汇报表.md", "S7 决策点汇报表"),
         ("09-审查报告.md", "S7 审查报告")]

def md2html(md):
    out, table, ul = [], [], False
    def flush_table():
        nonlocal table
        if not table: return
        rows = [r for r in table if not re.match(r"^\|[\s:\-|]+\|$", r)]
        h = ["<table>"]
        for i, r in enumerate(rows):
            cells = [c.strip() for c in r.strip().strip("|").split("|")]
            tag = "th" if i == 0 else "td"
            h.append("<tr>" + "".join(f"<{tag}>{inline(c)}</{tag}>" for c in cells) + "</tr>")
        h.append("</table>")
        out.append("\n".join(h)); table = []
    def inline(s):
        s = html.escape(s)
        s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
        return s
    for line in md.splitlines():
        if line.strip().startswith("|"):
            table.append(line); continue
        flush_table()
        if line.startswith(">"):
            out.append(f"<blockquote>{inline(line.lstrip('> '))}</blockquote>")
        elif line.startswith("#"):
            lvl = min(len(line) - len(line.lstrip('#')), 4)
            out.append(f"<h{lvl+1}>{inline(line.lstrip('# '))}</h{lvl+1}>")
        elif line.strip().startswith(("- ", "* ")):
            if not ul: out.append("<ul>"); ul = True
            out.append(f"<li>{inline(line.strip()[2:])}</li>")
        else:
            if ul: out.append("</ul>"); ul = False
            if line.strip(): out.append(f"<p>{inline(line)}</p>")
    if ul: out.append("</ul>")
    flush_table()
    return "\n".join(out)

def extract_table(md, after_kw):
    """取某关键词之后出现的第一张表（一页纸用）。"""
    seen = False; rows = []
    for line in md.splitlines():
        if after_kw in line: seen = True
        if seen and line.strip().startswith("|"): rows.append(line)
        elif seen and rows: break
    return md2html("\n".join(rows)) if rows else ""

CSS = """
body{font-family:'PingFang SC','Microsoft YaHei',sans-serif;margin:0;background:#f4f6fa;color:#222}
.wrap{max-width:1080px;margin:0 auto;padding:32px 20px}
.hero{background:linear-gradient(120deg,#e2231a,#ff6a3d);color:#fff;border-radius:14px;padding:28px 32px;margin-bottom:22px}
.hero h1{margin:0 0 6px;font-size:26px}.hero p{margin:0;opacity:.92}
.card{background:#fff;border-radius:12px;padding:22px 26px;margin-bottom:18px;box-shadow:0 2px 8px rgba(0,0,0,.06)}
.card h2{margin:0 0 12px;font-size:18px;border-left:4px solid #e2231a;padding-left:10px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}
table{border-collapse:collapse;width:100%;font-size:13px;margin:8px 0}
th,td{border:1px solid #d8dde6;padding:6px 9px;text-align:left;vertical-align:top}
th{background:#fff3f2}
h3,h4,h5{margin:14px 0 6px}blockquote{border-left:3px solid #ffb3a7;margin:6px 0;padding:4px 12px;color:#666;background:#fff8f7}
.badge{display:inline-block;background:#fff;color:#e2231a;border-radius:999px;padding:2px 12px;font-size:12px;font-weight:600;margin-right:8px}
details{margin-bottom:10px}summary{cursor:pointer;font-weight:600;padding:8px 0}
.onepager .card{border-top:3px solid #e2231a}
"""

def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(2)
    rd = sys.argv[1]
    docs = {}
    for f, _t in FILES:
        p = os.path.join(rd, f)
        if not os.path.exists(p):
            print(f"❌ 渲染失败：产物缺失 {f}"); sys.exit(1)
        docs[f] = open(p, encoding="utf-8").read()
    led = json.load(open(os.path.join(rd, "ledger.json"), encoding="utf-8")) if os.path.exists(os.path.join(rd, "ledger.json")) else {"activity": os.path.basename(rd)}
    name = led.get("activity", "活动方案")
    overview = md2html("\n".join(docs["07-产品方案.md"].split("## 2.")[0].splitlines()[1:]))
    onepager = f"""
<div class='onepager'>
 <div class='grid'>
  <div class='card'><h2>触发规则</h2>{extract_table(docs['03-活动规则.md'],'触发规则')}</div>
  <div class='card'><h2>逆向五场景</h2>{extract_table(docs['04-逆向方案.md'],'场景处理')}</div>
  <div class='card'><h2>曝光触点矩阵</h2>{extract_table(docs['05-曝光动线.md'],'矩阵')}</div>
  <div class='card'><h2>实验点盘点</h2>{extract_table(docs['06-成本与实验.md'],'盘点')}</div>
 </div>
 <div class='card'><h2>关键决策点（请示项）</h2>{extract_table(docs['08-决策点汇报表.md'],'决策点')}</div>
</div>"""
    full = "".join(
        f"<details {'open' if f=='07-产品方案.md' else ''}><summary>{t}</summary><div class='card'>{md2html(docs[f])}</div></details>"
        for f, t in FILES)
    page = f"""<!DOCTYPE html><html lang='zh'><head><meta charset='utf-8'>
<title>{name} · 方案可视化</title><style>{CSS}</style></head><body><div class='wrap'>
<div class='hero'><span class='badge'>评审版</span><h1>{name}</h1>{overview}</div>
<h2 style='margin:18px 4px'>一页纸 · 评审要点</h2>{onepager}
<h2 style='margin:18px 4px'>完整方案 · 分节展开</h2>{full}
</div></body></html>"""
    out = os.path.join(rd, "10-方案可视化.html")
    open(out, "w", encoding="utf-8").write(page)
    blocks = ["触发规则", "逆向五场景", "曝光触点矩阵", "实验点盘点", "关键决策点"]
    missing = [b for b in blocks if f"<h2>{b}" not in page or "<table>" not in page.split(f"<h2>{b}")[1][:2000]]
    if missing:
        print(f"❌ 关键区块缺表：{missing}"); sys.exit(1)
    print(f"✅ S8 渲染成功：{out}（关键区块 {len(blocks)} 个齐全）")

if __name__ == "__main__":
    main()

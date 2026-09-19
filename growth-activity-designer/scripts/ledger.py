#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生产台账：任务状态的唯一权威数据源。
- 一切状态读写经本脚本；Markdown 进度视图由 ledger.json 渲染、只读；
- 防跳步：advance 某步前，其全部前序步骤必须已 passed；
- 门禁联动：advance 自动调用对应门禁脚本，门禁不过状态不落账；
- 机械 diff：产物文件哈希入账，改动一目了然。

用法：
  python3 ledger.py init    <run_dir> <活动名>
  python3 ledger.py advance <run_dir> <S1..S8>
  python3 ledger.py status  <run_dir>
  python3 ledger.py diff    <run_dir>          # 对比产物当前哈希与入账哈希
"""
import hashlib, json, os, subprocess, sys, datetime

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

HERE = os.path.dirname(os.path.abspath(__file__))
STEPS = ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8"]
ARTIFACTS = {
    "S1": ["01-活动画像.md"],
    "S2": ["02-信息底座.md"],
    "S3": ["03-活动规则.md"],
    "S4": ["04-逆向方案.md"],
    "S5": ["05-曝光动线.md"],
    "S6": ["06-成本与实验.md"],
    "S7": ["07-产品方案.md", "08-决策点汇报表.md", "09-审查报告.md"],
    "S8": ["10-方案可视化.html"],
}
GATES = {  # 步骤 → 门禁脚本（S5 的触点校验并入 check_experiment，于 S6 执行）
    "S1": "check_brief.py", "S2": "check_context.py", "S3": "check_rules.py",
    "S4": "check_reverse.py", "S5": None, "S6": "check_experiment.py",
    "S7": "check_final.py", "S8": "render_report.py",
}

def lpath(run_dir):
    return os.path.join(run_dir, "ledger.json")

def load(run_dir):
    p = lpath(run_dir)
    if not os.path.exists(p):
        die(f"台账不存在，先 init：{p}")
    return json.load(open(p, encoding="utf-8"))

def save(run_dir, led):
    json.dump(led, open(lpath(run_dir), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    render(run_dir, led)

def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:12]

def die(msg):
    print(f"❌ ledger：{msg}"); sys.exit(1)

def init(run_dir, name):
    os.makedirs(run_dir, exist_ok=True)
    if os.path.exists(lpath(run_dir)):
        die("台账已存在，禁止覆盖（防误初始化）")
    led = {"activity": name, "created": now(),
           "steps": {s: {"status": "pending", "artifacts": {}, "ts": None} for s in STEPS}}
    save(run_dir, led); print(f"✅ 台账初始化：{name}")

def advance(run_dir, step):
    if step not in STEPS:
        die(f"未知步骤 {step}")
    led = load(run_dir)
    idx = STEPS.index(step)
    blocked = [s for s in STEPS[:idx] if led["steps"][s]["status"] != "passed"]
    if blocked:
        die(f"防跳步：前序未完成 {blocked}")
    # v2 修复：先跑门禁、后验产物——S8 的产物由门禁脚本（渲染器）生成，
    # 原顺序（先验产物再跑门禁）在 S8 上形成鸡生蛋死锁。门禁自会校验各自输入。
    gate = GATES[step]
    if gate:
        r = subprocess.run([sys.executable, os.path.join(HERE, gate), run_dir],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        print(r.stdout.strip())
        if r.returncode != 0:
            print(r.stderr.strip()); die(f"{step} 门禁不通过，状态不落账")
    for a in ARTIFACTS[step]:
        if not os.path.exists(os.path.join(run_dir, a)):
            die(f"产物缺失：{a}")
    led["steps"][step] = {"status": "passed", "ts": now(),
                          "artifacts": {a: sha(os.path.join(run_dir, a)) for a in ARTIFACTS[step]}}
    save(run_dir, led); print(f"✅ {step} 通过并入账")

def status(run_dir):
    led = load(run_dir)
    for s in STEPS:
        st = led["steps"][s]
        print(f"{s}: {st['status']:8s} {st['ts'] or ''}")

def diff(run_dir):
    led = load(run_dir); changed = []
    for s in STEPS:
        for a, h in led["steps"][s].get("artifacts", {}).items():
            p = os.path.join(run_dir, a)
            if os.path.exists(p) and sha(p) != h:
                changed.append(f"{s}/{a}（入账 {h} → 当前 {sha(p)}）")
    if changed:
        print("⚠️ 产物在入账后被修改（需重跑对应门禁重新入账）：")
        [print("  -", c) for c in changed]
        sys.exit(1)
    print("✅ 全部产物与台账一致")

def render(run_dir, led):
    lines = [f"# 进度视图（只读，由 ledger.json 渲染，勿手改）",
             f"\n活动：{led['activity']} ｜ 渲染时间见 ledger.json\n",
             "| 步骤 | 状态 | 通过时间 | 产物（哈希） |", "|---|---|---|---|"]
    for s in STEPS:
        st = led["steps"][s]
        arts = "<br>".join(f"{a} `{h}`" for a, h in st.get("artifacts", {}).items()) or "—"
        lines.append(f"| {s} | {st['status']} | {st['ts'] or '—'} | {arts} |")
    open(os.path.join(run_dir, "进度视图.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")

def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(2)
    cmd, rd = sys.argv[1], sys.argv[2]
    if cmd == "init":
        init(rd, sys.argv[3] if len(sys.argv) > 3 else os.path.basename(rd))
    elif cmd == "advance":
        advance(rd, sys.argv[3])
    elif cmd == "status":
        status(rd)
    elif cmd == "diff":
        diff(rd)
    else:
        die(f"未知命令 {cmd}")

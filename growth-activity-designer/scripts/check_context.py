#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""S2 门禁：每条信息有来源与动静分层；动态件必须有取数口径或列入索取清单。"""
import re
from gates_common import load, need, fail, ok, run_dir_from_argv

d = run_dir_from_argv("check_context")
t = load(d, "02-信息底座.md")
need(t, ["来源"], "信息底座必须逐条标注来源")
need(t, ["静态", "动态"], "必须体现动静分层")
rows = [l for l in t.splitlines() if l.strip().startswith("|") and "---" not in l]
if len(rows) < 5:
    fail(f"信息条目过少（{len(rows)} 行），疑似未按信息量地图逐件装载")
dyn = [l for l in rows if "动态" in l]
bad = [l[:30] for l in dyn if not re.search(r"取数|口径|索取|BI|导出", l)]
if bad:
    fail(f"动态信息件缺取数口径/索取路径：{bad}")
if "索取清单" not in t:
    fail("缺『索取清单』一节（无缺失项也要写明'无'）")
ok("S2", f"信息件 {len(rows)} 条，动态 {len(dyn)} 条均带取数口径")

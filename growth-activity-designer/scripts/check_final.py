#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""S7 门禁：方案模板十段齐全；决策点汇报表可拍板；审查报告零未通过项。"""
import re
from gates_common import load, need, fail, ok, run_dir_from_argv

d = run_dir_from_argv("check_final")
t7 = load(d, "07-产品方案.md")
secs = ["活动概述", "业务背景", "玩法选型", "活动规则", "逆向", "曝光动线", "成本", "实验计划", "决策点", "边界声明"]
missing = [s for s in secs if s not in t7]
if missing:
    fail(f"方案模板段落缺失：{missing}")
t8 = load(d, "08-决策点汇报表.md")
need(t8, ["请示|开放问题"], "决策点汇报表缺请示项列")
rows8 = [l for l in t8.splitlines() if l.strip().startswith("|") and "---" not in l and "决策点" not in l]
if len(rows8) < 5:
    fail(f"决策点汇报表行数过少（{len(rows8)}），每个需求模块至少一行")
t9 = load(d, "09-审查报告.md")
if re.search(r"不通过", t9):
    fail("审查报告存在未通过项，清零后才放行")
n_pass = len(re.findall(r"通过|不适用", t9))
if n_pass < 8:
    fail(f"审查项不足 8 条（当前 {n_pass}）")
ok("S7", f"模板十段齐全、汇报表 {len(rows8)} 行、审查 8 项清零")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""S3 门禁：候选对比有排除理由；触发规则四字段带口径；杠杆参数留实验位；互斥扫描全覆盖。"""
import re
from gates_common import load, need, fail, ok, run_dir_from_argv

d = run_dir_from_argv("check_rules")
t = load(d, "03-活动规则.md")
need(t, ["候选", "排除"], "缺候选玩法对比或排除理由")
for f in ["动作", "命中条件", "发奖条件", "奖励"]:
    if f not in t:
        fail(f"触发规则缺字段：{f}")
# v3：消费型口径项支持显式豁免——"不适用：<理由>"才放行，留白仍硬停
# （联调发现门禁过拟合消费型玩法：访问型动作无商品池/金额口径，但豁免必须声明理由，不许静默跳过）
need(t, ["含.{0,6}赠金|不含.{0,6}赠金|本金|金额口径.{0,4}不适用"], "金额口径未写明含/不含赠金（消费型必填；非消费型写『金额口径不适用：理由』）")
need(t, ["排除清单|特殊商品|虚拟|预售|商品池.{0,4}不适用"], "商品池口径缺特殊商品排除说明（消费型必填；非消费型写『商品池不适用：理由』）")
# 只在「杠杆参数」小节内检查（v2 修复：全篇匹配会把叙述句里的"档位/门槛"误判为参数行）
m = re.search(r"##\s*杠杆参数([\s\S]*?)(?=\n## |\Z)", t)
if not m:
    fail("缺『杠杆参数』小节（所有杠杆必须集中声明并标实验位）")
lev_rows = [l for l in m.group(1).splitlines() if l.strip().startswith(("-", "|")) and len(l.strip()) > 5]
no_exp = [l.strip()[:40] for l in lev_rows if "实验位" not in l and "不实验" not in l]
if no_exp:
    fail(f"杠杆参数行未标实验位：{no_exp}")
need(t, ["互斥"], "缺互斥扫描")
need(t, ["权益冲突", "场景冲突"], "互斥扫描必须含权益冲突与场景冲突两判据")
if not re.search(r"覆盖率\s*100%|逐条|全部在投", t):
    fail("互斥扫描未声明覆盖在投清单 100%")
ok("S3", "候选/触发四字段/实验位/互斥双判据齐全")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""S1 门禁：活动画像四段齐全、带口径、零玩法预设。"""
from gates_common import load, need, fail, ok, run_dir_from_argv

d = run_dir_from_argv("check_brief")
t = load(d, "01-活动画像.md")
need(t, ["北极星", "护栏"], "第一问缺失（北极星/护栏）")
need(t, ["口径"], "指标必须带口径（分母/统计周期）")
need(t, ["人群"], "第二问缺失（目标人群与量级）")
need(t, ["资源|权益"], "第三问缺失（可投入资源）")
need(t, ["底线|上限|红线"], "第四问缺失（不可破底线）")
for banned in ["返比", "档位", "中奖率"]:
    if banned in t:
        fail(f"画像阶段出现玩法参数「{banned}」——S1 只问业务问题，玩法是 S3 的事")
ok("S1", "四段齐全、带口径、无玩法预设")

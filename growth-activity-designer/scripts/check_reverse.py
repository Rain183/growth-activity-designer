#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""S4 门禁：逆向五场景全覆盖 + 结构性判据有结论。缺一场景硬停。"""
from gates_common import load, need, fail, ok, run_dir_from_argv

d = run_dir_from_argv("check_reverse")
t = load(d, "04-逆向方案.md")
scenes = {
    "部分退款仍达标/满足门槛": ["仍达标|仍满足|仍满"],
    "部分退款不再达标": ["不再达标|不再满足|不满足|回滚|回收资格|回收对应"],
    "用奖后退款": ["用奖|已用|已兑换|追回"],
    "边界时间套利": ["边界时间|临过期|延期"],
    "机器与批量薅羊毛": ["批量|机器|薅|风控"],
}
import re
missing = [k for k, pats in scenes.items() if not any(re.search(p, t) for p in pats)]
if missing:
    fail(f"逆向场景缺失（5 缺 {len(missing)}）：{missing}")
need(t, ["结构|拆分|追回能力"], "缺结构性判据结论（奖励结构是否支持部分追回）")
need(t, ["文案|感知|挽留"], "缺用户感知文案要点")
ok("S4", "五场景全覆盖+结构性判据+文案要点")

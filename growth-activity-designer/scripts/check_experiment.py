#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""S5+S6 门禁：触点覆盖与红线；成本公式可复算；实验点盘点、对照设计、护栏、样本量。"""
import re
from gates_common import load, need, fail, ok, run_dir_from_argv

d = run_dir_from_argv("check_experiment")
t5 = load(d, "05-曝光动线.md")
need(t5, ["私域", "公域"], "触点未覆盖私域+公域")
need(t5, ["状态|矩阵"], "缺用户状态维度（触点矩阵）")
need(t5, ["前置条件|红线|不呈现"], "触点缺前置条件/红线标注")
t6 = load(d, "06-成本与实验.md")
if not re.search(r"[=×x\*]", t6):
    fail("成本测算无公式（必须可复算）")
need(t6, ["盘点|功能型|效果型"], "缺实验点盘点（功能型/效果型）")
need(t6, ["对照"], "缺对照组设计")
need(t6, ["护栏"], "缺护栏指标")
need(t6, ["样本量|流量.{0,6}反推|显著"], "缺样本量测算/显著性口径")
need(t6, ["锁组|全周期"], "周期型活动必须声明用户级分流+全周期锁组（非周期型标不适用）")
ok("S5/S6", "触点矩阵+红线、公式、盘点、对照、护栏、样本量齐全")

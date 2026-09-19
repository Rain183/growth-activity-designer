#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""门禁公共库：读产物、按规则校验、统一输出。产物缺失或不合格 → exit 1（硬停）。"""
import os, re, sys

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

def load(run_dir, fname):
    p = os.path.join(run_dir, fname)
    if not os.path.exists(p):
        fail(f"产物缺失：{fname}（流程停在当前步，先补产物）")
    t = open(p, encoding="utf-8").read()
    if len(t.strip()) < 80:
        fail(f"产物疑似空壳：{fname}（{len(t)} 字符）")
    return t

def need(text, patterns, msg):
    """patterns: list[str regex]，全部命中才过。"""
    missing = [p for p in patterns if not re.search(p, text)]
    if missing:
        fail(f"{msg}；未命中要素：{missing}")

def fail(msg):
    print(f"❌ 门禁不通过：{msg}")
    sys.exit(1)

def ok(step, msg):
    print(f"✅ {step} 门禁通过：{msg}")
    sys.exit(0)

def run_dir_from_argv(step):
    if len(sys.argv) < 2:
        print(f"用法：python3 {step}.py <运行目录路径，如 ../runs/活动名>")
        sys.exit(2)
    d = sys.argv[1]
    if not os.path.isdir(d):
        fail(f"运行目录不存在：{d}")
    return d

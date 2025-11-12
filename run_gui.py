#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Launcher for GitRecombo Desktop GUI
Run this from the repository root: python run_gui.py
"""
import sys
from pathlib import Path

# Add gitrecombo folder to path
repo_root = Path(__file__).parent
sys.path.insert(0, str(repo_root))

if __name__ == "__main__":
    from gitrecombo.desktop_gui import GitRecomboGUI
    app = GitRecomboGUI()
    app.run()

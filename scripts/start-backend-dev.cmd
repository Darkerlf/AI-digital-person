@echo off
cd /d "D:\AI digital person\.worktrees\admin-backend-phase1\backend"
"D:\ProgramData\condaData\envs_dirs\dev_envs_1\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > "D:\AI digital person\.worktrees\admin-backend-phase1\logs\backend-uvicorn.cmd.log" 2>&1

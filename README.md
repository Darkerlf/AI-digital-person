# Scenic Admin Backend

Task 1 bootstrap for the admin backend and planned Vue admin frontend.

## Local Development Notes

- Preferred Python interpreter: `D:\ProgramData\condaData\envs_dirs\dev_envs_1\python.exe`
- Use this interpreter when creating or repairing the backend virtual environment to avoid forgetting the team standard path.

## Backend

```powershell
cd backend
& 'D:\ProgramData\condaData\envs_dirs\dev_envs_1\python.exe' -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
Copy-Item ..\.env.example .env
.\.venv\Scripts\python scripts/init_db.py
.\.venv\Scripts\python -m uvicorn app.main:app --reload
```

## Frontend

```powershell
cd admin-web
npm.cmd install
npm.cmd run dev
```

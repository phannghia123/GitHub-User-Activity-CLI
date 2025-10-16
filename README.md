# Task Tracker

A tiny Python task tracker stored in JSON. Files in this repo:

- `task.py` — core application (task management).
- `tasks.json` — local data file with your tasks.

How to push this project to GitHub (PowerShell)

1. Inspect and adjust `.gitignore` if needed (already included).

2. Initialize a local repo, add and commit:

```powershell
cd E:\Task_Tracker
git init
git add .
git commit -m "Initial commit"
```

3. Create a remote repository on GitHub:

- Option A — GitHub website: create a new repo, then copy the HTTPS or SSH remote URL.
- Option B — GitHub CLI (if installed):

```powershell
gh repo create my-username/task-tracker --public --source=. --remote=origin --push
```

4. Or add the remote manually and push (HTTPS example):

```powershell
git remote add origin https://github.com/<USERNAME>/<REPO>.git
git branch -M main
git push -u origin main
```

SSH example (if you have an SSH key on GitHub):

```powershell
git remote add origin git@github.com:<USERNAME>/<REPO>.git
git branch -M main
git push -u origin main
```

Notes

- `tasks.json` currently contains personal task items. Confirm you want it tracked before pushing. Remove or add it to `.gitignore` if you prefer it private.
- If you need help creating the remote repo or running the commands, tell me and I can run the safe local commands for you (init/add/commit) or walk through `gh` steps.

That's it — tell me whether to initialize git locally now, or if you want me to push (you'll need to provide credentials or use `gh`).

Roadmap

You can find a related task-tracker roadmap here:

https://roadmap.sh/projects/task-tracker

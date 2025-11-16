# Crowd-Source Civic Issue Reporting and Resolution System

A Python-based civic complaint management and automation system for registering, processing, and tracking citizen complaints. The project provides a small Flask application with structured workflows, role-based views (citizen, municipal staff, admin), and tests to help validate behavior.

## Team Members

- Harsh Chauhan
- Atharva Bhuse
- Amruta Konnapure
- Dr. Mansi Bhonsle

## Key Features

- Submit and track complaints through a web UI
- Role-based dashboards for citizens, municipal officers, and administrators
- File uploads and attachments for complaints
- Reporting and basic statistics pages
- Tests covering core flows (pytest)

## Repository layout

- `civic_complaint_system/` — main application package (Flask app, routes, models)
- `instance/` — runtime instance files (SQLite DB, local config)
- `static/`, `templates/` — web assets and templates
- `requirements.txt` — Python dependencies
- Test files are included under `civic_complaint_system/` (pytest)

## Quickstart (development)

Prerequisites:

- Python 3.8+ installed
- Git (optional, for development)

1. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate    # Git Bash / macOS / Linux
# On Windows PowerShell: .\\venv\\Scripts\\Activate.ps1
# On Windows (cmd): .\\venv\\Scripts\\activate.bat
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Configure environment

Create an `instance/` directory if it doesn't exist and ensure the Flask config can read it. The project may use `instance/config.py` or `civic_complaint_system/config.py` for settings. Example environment variables:

```bash
export FLASK_APP=civic_complaint_system.app
export FLASK_ENV=development
# On Windows (PowerShell): setx FLASK_APP "civic_complaint_system.app"
```

4. Initialize / migrate the database

This project uses an SQLite database in `instance/`. If there is no migration tool in the repo, you can create the initial database using the app's models. Example (adjust to your project layout):

```bash
python -c "from civic_complaint_system import app, models; import os; os.makedirs('instance', exist_ok=True); models.db.create_all(app=app)"
```

Note: the repository currently contains `instance/complaints.db`. For development you may want to remove this from the git history or replace it with a sample fixture. See "Repository hygiene" below.

5. Run the app

```bash
flask run
# or
python -m flask run
```

Open http://127.0.0.1:5000 in your browser.

## Running tests

The repository includes several test files (pytest). Run the test suite with:

```bash
pip install -r requirements.txt   # ensure pytest is installed
pytest -q
```

## Repository hygiene — remove committed local database

The repo includes a committed SQLite database at `instance/complaints.db`. This file often contains local or sensitive data and should not be tracked in source control.

To stop tracking it and add it to `.gitignore`:

```bash
git rm --cached instance/complaints.db
echo "instance/complaints.db" >> .gitignore
git add .gitignore
git commit -m "Remove local DB and ignore it"
git push
```

If you need the file removed from the repository history entirely (so it never appears in any commit), use `git filter-repo` or `git filter-branch`. Ask for help and I can provide the precise commands.

## Contributing

- Fork the repository and open a pull request with clear changes
- Add tests for new functionality
- Keep secrets out of the repo (API keys, DB files)

## Troubleshooting

- If Flask can't find the app, ensure `FLASK_APP` points to `civic_complaint_system.app` or run `python -m civic_complaint_system.app` directly.
- If database errors occur, delete `instance/complaints.db` (after backing up) and recreate it with the model commands above.

## License & Contact

Include your preferred license here (MIT, Apache-2.0, etc.).

Maintainer: Harsh Chauhan — replace with a preferred contact email or profile.

---

If you'd like, I can:

- remove `instance/complaints.db` from history safely,
- add a sample `instance/seed_data.sql` or fixtures,
- add a GitHub Actions workflow to run tests on push.

Tell me which of those you'd like next.

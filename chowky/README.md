# Chowky

Hyperlocal + interest-community social app. Pick your area, get fun updates,
news, confessions, and chitchat from people around you — plus interest-based
"Tribes" (Running, Reading, Trekking, etc.) scoped per city.

## Setup (local dev)

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy the example env file and fill in a secret key
cp .env.example .env
# edit .env — set FLASK_SECRET_KEY to any long random string

# 4. Initialize the local SQLite database (creates app/chowky.db)
python scripts/init_db.py

# 5. Run the app
python run.py
```

Visit `http://127.0.0.1:5000` — you should be redirected to the login page.
Click "Create an account" to sign up, then log in.

## What's working right now

- Signup (email, pseudonym, password — hashed with werkzeug)
- Login / logout (session-based)
- Database schema for cities, zones, users, tribes, tribe_members, posts,
  comments, likes, reports — pre-seeded with Mumbai, Pune, Thane, Navi Mumbai,
  Panvel, Latur, Delhi, Bangalore, Hyderabad, Chennai, Kota, plus zones for
  Navi Mumbai, Panvel, and Pune, and starter tribes for Pune.

## What's next (see chowky_project_structure.md for the full build order)

1. Onboarding — city/zone selection after signup
2. Zone feed + post composer (the core loop)
3. Likes, comments, report/auto-hide
4. Tribes — join/leave, tribe feed
5. Admin — moderation queue
6. Dockerize + deploy to Render

## Deployment (Render)

1. Push this repo to GitHub.
2. On Render: New → Web Service → connect the repo.
3. Add a managed PostgreSQL instance, copy its connection string into the
   `DATABASE_URL` environment variable in your Render Web Service settings.
4. Set `FLASK_ENV=production` and `FLASK_SECRET_KEY` in Render's environment
   variables too.
5. Run `schema.sql` (the Postgres version) against the Render Postgres
   instance once, to create tables — e.g. via `psql` connected to the
   Render database URL.
6. Render auto-builds and redeploys on every push once connected.

## Notes

- `schema.sql` = Postgres (production). `schema_sqlite.sql` = SQLite (local
  dev). Keep both in sync manually if you change the schema.
- Passwords are hashed with `werkzeug.security` — never stored in plaintext.
- All queries use parameterized placeholders (`?` for SQLite, `%s` for
  Postgres, handled automatically via `app/db.py`'s `placeholder()`) —
  never string-format user input into SQL.

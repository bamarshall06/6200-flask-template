# Working in this project

This is a student project for **DATA 6200** at Georgia College — a Flask app
deployed to a Dokku server called iscs2. Read this before writing or changing
anything here.

**The person you are helping is learning this, and is graded on understanding
it — not on the code existing.** They record a video walking through their own
project and explaining it. So when you change something, say in one or two
plain sentences what you changed and why it works. Do not refactor beyond what
was asked, do not introduce a pattern the project is not already using, and do
not do in three files what the project does in one. A student cannot walk
through code they have never seen the shape of.

## One of everything, and it already exists

This is the rule most likely to be got wrong, because the undergraduate
sections of this kit work differently.

A 6200 student has **one** Dokku app, **one** port, **one** MySQL database and
**one** GitHub repository, for the entire course. All four already exist by the
time this kit is in use.

- **Never run or suggest `apps:create`.** The app was created for them. Its
  name is on the **Deployments** page in the course sidebar, and in
  `my-server.json`.
- **Never suggest "Use this template"** after Module 6. The student's repository
  was created from this kit once, in **HTML + the Pipeline**, and holds graded
  work and the history behind their live site. A second repository strands both.
  If this kit's files are already present — and in a student's repo they always
  are — there is nothing to install and nothing to migrate.
- **Never create a database.** It was created together with the app and carries
  the same name with dashes turned into underscores.
- The app name is the student's netid with dots turned into dashes, plus
  `-6200`. The server refuses any other name.

The module names in this course are **HTML + the Pipeline**, **Flask +
Routes**, **Database + SQL** and **Deploy & Secure**. It does not use the
numbered "Module 3 / Module 4" scheme the undergraduate sections do; if you
find that numbering in a file here, it is a leftover and it is wrong.

## `my-server.json`, and the one thing that must never go in it

`my-server.json` holds the student's app name, port, live URL, GitHub repo and
database coordinates. **Read it when you need any of those** rather than asking
the student to retype them.

**Never write a password, a `DATABASE_URL`, or any other secret into it.** That
file is committed. Credentials go in `.env` (git-ignored) locally and in
`config:set` on the server, and nowhere else — the student's code reads
`DATABASE_URL` and never contains it.

`check_server.py` validates that file against the live server and **fails if it
finds a secret in it**. If a student reports it failing that check, the fix is
to remove the secret, rotate it (`ssh dokku@iscs2.gcsu.edu mysql:rotate <app>`)
and set the new value in the two correct places. Do not loosen the check.

`check_server.py` is read-only and safe to run at any time. When a student says
deploying or the database "isn't working", run it first — it checks the boring
things (a typo in a port, a missing remote, a `.env` that disagrees) before
anyone debugs application code.

## What this is

A Flask application: a Python program that runs on a server, decides what each
page says, and hands the browser finished HTML.

**Flask + Routes has no database.** `DATABASE_URL`, `.env`, the `database/`
folder and the Examples page are all **Database + SQL** onward. Until a
`DATABASE_URL` exists the app runs perfectly well without one, and the Examples
page says so rather than crashing. Do not "fix" that, and do not add a database
to a project that has not asked for one.

## Running it

Once per project:

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Then every time:

```bash
source venv/bin/activate        # Windows: venv\Scripts\activate
python app.py
```

It serves <http://127.0.0.1:5000>. Leave it running while editing — Flask
reloads itself when a `.py` file is saved; a template or CSS change just needs a
browser refresh. `Ctrl-C` stops it.

If the prompt does not start with `(venv)` the activate line did not run, and
`python app.py` fails with `ModuleNotFoundError: No module named 'flask'`. That
is the single most common problem in this project. Check it first.

## What each file is

| File | What it does |
|---|---|
| `app.py` | The app: one function per page, each with an `@app.route` above it. Blueprints are registered here |
| `my-server.json` | The student's app name, port, URL and database coordinates. **No secrets** |
| `check_server.py` | Validates that file against the live server. Read-only |
| `templates/base.html` | The navbar and footer every page shares. The student's name goes here, and one Bootstrap `bg-*` class sets the navbar colour |
| `templates/index.html`, `about.html` | The content pages. They `extend` base.html rather than repeating it |
| `static/css/style.css` | The student's styles. Almost empty on purpose |
| `requirements.txt` | The packages this app needs |
| `Procfile`, `gunicorn.conf.py`, `runtime.txt` | How the class server runs the app. **Do not change these** |
| `.env.example`, `database/`, `blueprints/examples.py` | **Database + SQL** onward. Not used before then |

**A route and a template are two halves of one page.** `app.py` decides *what*
the page says; the file in `templates/` decides *how it looks*. Changing the
wrong half produces no visible effect, and that is the most common confusion in
this project after the venv. When a change appears to do nothing, check which
half was edited.

## Layout

Flat. No `app/` package, no application factory, no ORM.

```
app.py            the Flask app: plain @app.route pages, and blueprint registration
my-server.json    the student's server details
check_server.py   checks those details against reality
database/         connection.py, plus schema.sql and seed_data.sql
blueprints/       one file per group of related pages
templates/        all Jinja templates, flat
static/css/       style.css
```

## Database

- Import it as `from database import get_connection`.
- `get_connection()` opens a **new** connection every call, and the caller
  closes it, in a `finally` block. Never cache one on `g`, never open one in a
  `before_request` hook.
- Use `conn.cursor(dictionary=True)` so rows come back as dicts. This project
  uses `mysql-connector-python`, not PyMySQL — `dictionary=True` is a
  `TypeError` on PyMySQL, so do not switch drivers.
- Use `%s` placeholders and pass the values as a tuple. Never build SQL with an
  f-string or string concatenation.
- Call `conn.commit()` after INSERT, UPDATE and DELETE.
- **Never add a "is the database configured?" check inside a route.** If there
  is no database, `get_connection()` raises `DatabaseNotConfigured` and `app.py`
  turns that into a friendly 503 page. That is deliberate: it keeps every
  blueprint clean enough to be copied as-is.
- **The database host is `172.17.0.1`, not `localhost`.** The app runs in a
  container, where `localhost` means the container. A consequence worth stating
  to the student rather than debugging: **the same `DATABASE_URL` cannot connect
  from their laptop.** Data-backed pages are tested on the live site. A MySQL
  error that appears only locally is expected and is not a bug.

## Blueprints

- One file per feature: `blueprints/<thing>.py`.
- It defines `<thing>_bp = Blueprint("<thing>", __name__)`.
- Routes carry their own prefix (`@<thing>_bp.route("/<thing>")`), and `app.py`
  registers it with no `url_prefix`.
- Register it in `app.py`, and add a link in `templates/base.html`.
- When a new blueprint is asked for, base it on `blueprints/examples.py`. That
  file exists to be copied.

## Configuration

- Read environment variables inside functions, never at module import time.
- `DATABASE_URL` and `FLASK_SECRET_KEY` are the only two. Do not invent more
  without being asked.
- Never commit `.env`, and never put a password in a file git tracks.
  `.gitignore` already blocks `.env` — leave that line in place.

## Deploying

Two remotes, two different jobs, and **both** are needed every time.

| Remote | What it is for |
|---|---|
| `origin` | GitHub. The code and its history. This is what gets graded |
| `dokku` | The class server. This is what makes the site live |

The app already exists, so there is one remote to add and nothing to create:

```bash
git remote add dokku dokku@iscs2.gcsu.edu:<their-app-name>

# every time the live site should catch up
git add .
git commit -m "Add the routes"
git push origin main    # the code, to GitHub
git push dokku main     # the site, to the class server
```

Pushing to `origin` does not update the live site, and pushing to `dokku` does
not save the work to GitHub. Both, every time.

`/healthz` on the live site proves the app is up, and reports whether
`DATABASE_URL` was actually picked up — useful because students are not allowed
to run `config:show`. If the site does not answer at all, the app may be
stopped: `ssh dokku@iscs2.gcsu.edu ps:start <app>`.

## When something breaks

| What they see | What it means | What to do |
|---|---|---|
| `ModuleNotFoundError: No module named 'flask'` | The venv is not active | Look for `(venv)` in the prompt; re-run the activate line |
| `Address already in use` | An older `python app.py` is still running | `Ctrl-C` it, or close that terminal |
| `jinja2.exceptions.TemplateNotFound` | The name in `render_template(...)` does not match the file in `templates/` | Compare the two, including the `.html` |
| `Permission denied (publickey)` | Their SSH key is not registered on iscs2 yet | **HTML + the Pipeline**, Lesson 6; not a code problem |
| `repository ... does not exist` | The `dokku` remote has the wrong app name — dots instead of dashes, or not their own | `python check_server.py` names the correct one |
| `Everything up-to-date`, but the site is unchanged | Nothing was committed | `git add .` then `git commit` first |
| Deploy succeeds, site does not respond | `Procfile` misspelled — capital P, no extension | Check the filename, not the contents |
| Site does not respond at all | The app may be stopped | `ssh dokku@iscs2.gcsu.edu ps:start <app>` |
| A "No database yet" page | Expected before **Database + SQL** | Leave it alone. After that, `DATABASE_URL` is not set on the server |
| `Access denied` from MySQL | Wrong password, or it contains `@ / # +` and was not percent-encoded | Percent-encode it (`@` becomes `%40`) |
| MySQL errors on their laptop only | Expected — `172.17.0.1` exists only on the server | Test data-backed pages on the live site |
| Anything else on the live site | — | `ssh dokku@iscs2.gcsu.edu logs <app-name>` |

## What not to change

`Procfile`, `gunicorn.conf.py` and `runtime.txt` are tuned for the class
server: a 256 MB container with half a CPU, and a pinned Python version so a
build that works in October still works in December. Changing them is how a
deploy stops working for reasons that are hard to find.

`requirements.txt` lists only what is actually imported. Do not add packages
speculatively, and do not run `pip freeze` into it.

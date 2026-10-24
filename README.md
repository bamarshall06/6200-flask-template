# Flask Kit — DATA 6200

The Flask kit for **DATA 6200**, and the starting point for the one project you
build all semester. It is a working website from the first minute: a Python
program that decides what each page says and hands the browser finished HTML.

You start using it in **HTML + the Pipeline**, before any of it is explained.
**Flask + Routes** is where it gets explained.

## Read this first: use this template once, in Module 6

In **HTML + the Pipeline** you click the green **Use this template** button at
the top of this page and create **one private repository** named
`lastname-6200-project-06`. That repository is yours for the whole course.

**Click it once and never again.** You keep **one repository, one app, one port
and one database** from October to December. Making a second repository later
would strand your graded work and your live site in the first one — so if
anything tells you to use this template again, it is out of date.

By **Flask + Routes** this kit is already in the repository you have been
deploying for a week. There is nothing to install and nothing to migrate.

## One of everything, for the whole course

| You get | How many | Where it comes from |
|---|---|---|
| Dokku app | **one** | Made for you. Find its name on **Deployments** in the course sidebar |
| Port | **one** | Assigned to you. Also on **Deployments** |
| MySQL database | **one** | Made *with* your app, carrying the same name |
| GitHub repo | **one** | Created from this template in **HTML + the Pipeline** |

This is different from the undergraduate sections, and it is deliberate: the
project you deploy this week is the same project you are still deploying in
**Deploy & Secure**. Nothing here is throwaway.

**You never run `apps:create`.** Your app already exists. If a lesson or an
agent tells you to create one, it is reading the undergraduate instructions.

## `my-server.json` — where your server details live

You get one app, one port and one database, and you will need their details
dozens of times between now and December. They go in **`my-server.json`**, in
this project, so they travel with the work and are never more than one file
away.

Fill it in from the **Deployments** page. Then:

```bash
python check_server.py
```

That reads the file and checks it against reality — are the values consistent
with each other, do your git remotes match, does your live site answer, does
your `.env` agree. Every failure line says what is wrong and how to fix it. It
only ever reads; it changes nothing, so run it as often as you like.

Most of the file is not a free choice, which is why the checker can catch a
typo:

- your **app name** is your netid with dots turned into dashes, plus `-6200`
- your **database name** is your app name with dashes turned into underscores
- your **database username** is the database name
- your **live URL** is `https://iscs2.gcsu.edu:` plus your port

Only the port is handed to you.

> ### Your database password does not go in this file
>
> `my-server.json` **is committed**, and that is safe — a port appears in your
> URL and a database name appears in your logs. Neither is a secret.
>
> A password is. It goes in exactly two places, neither of which git tracks:
> `.env` on your laptop, and `config:set` on the server. Your code reads
> `DATABASE_URL` and never contains it.
>
> `check_server.py` fails if it finds a password or a connection string in
> `my-server.json`, because a secret in a tracked file is the one mistake in
> this course that cannot be taken back — automated scanners read public GitHub
> within hours of a push.

## Getting it running

Once per project, make a virtual environment and install the packages:

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate
# Windows
venv\Scripts\activate

pip install -r requirements.txt
```

Then, every time you work on it:

```bash
source venv/bin/activate    # Windows: venv\Scripts\activate
python app.py
```

Open <http://127.0.0.1:5000>. Home, About and the error pages all work.

Leave it running while you edit. Flask reloads itself when you save a `.py`
file; for a template or CSS change just reload the browser tab. `Ctrl-C` stops
it.

If your prompt does not start with `(venv)`, the activate line did not run, and
`python app.py` will fail with `ModuleNotFoundError: No module named 'flask'`.

**No database yet.** In **Flask + Routes** the app runs with no configuration at
all. The Examples page says it has no database — that is correct, leave it
alone until **Database + SQL**.

## What each file is

| File | What it does |
|---|---|
| `app.py` | The app itself: one function per page, each with a `@app.route` above it. **Your routes go here** |
| `my-server.json` | **Your app name, port, URL and database.** Yours to fill in. No passwords |
| `check_server.py` | Checks that file against the real server. Read-only |
| `templates/base.html` | The navbar and footer every page shares. **Your name goes in it**, and one Bootstrap class sets the navbar colour |
| `templates/index.html`, `about.html` | Your content pages. They `extend` base.html rather than repeating it |
| `static/css/style.css` | Your styles. Almost empty on purpose |
| `requirements.txt` | The packages your app needs |
| `Procfile`, `gunicorn.conf.py`, `runtime.txt` | How the class server runs your app. Leave these alone |
| `CLAUDE.md` | The rules Claude Code follows in this project. Worth reading once |
| `.env.example`, `database/`, `blueprints/examples.py` | *Database + SQL onward.* Not used yet |
| `database/schema.md` | **Why your schema is shaped that way.** Graded in *Database + SQL* |
| `docs/aws.md`, `docs/security.md` | **Your deploy write-up and your security report.** Graded in *Deploy & Secure* |
| `analysis/` | **Your script, chart and findings.** Graded in *Python + Big Data* |

A route and a template are two halves of one page. `app.py` decides *what* the
page says; the template in `templates/` decides *how it looks*. Change the
wrong half and nothing happens — that is the most common confusion in this
project, after the venv.

## How it works

**This section is graded, and it is yours to write.** *Flask + Routes* reads it
for **"Traces one request end to end"**, and *Database + SQL* reads it for the
full browser-to-response chain and for your proof the page is really
data-backed.

Replace all of it. Write it for someone who has never seen this project — being
able to do that is the difference between understanding what you built and
having assembled it.

### One request, traced

A visitor types `TODO`, and then what?

| Step | What happens here |
|---|---|
| The URL | `TODO` |
| The route that matched | `TODO` in `app.py` |
| The function that ran | `TODO` |
| The template it rendered | `templates/TODO` |
| One value Python put in | `TODO` |

### The database chain *(Database + SQL onward)*

Browser → route → query → response, named at each step. TODO

### Proof it is really data-backed

**Which row you changed, and what changed on the page as a result — with no code
edit.** This is the criterion people most often assert instead of showing, so
show it.

TODO

## Configuration

**Names, never values.** Every variable this project reads, and where its value
actually lives — which is never this repository.

| Variable | What it is | Where the value lives |
|---|---|---|
| `DATABASE_URL` | The connection string for your MySQL database | your gitignored `.env` locally, and `config:set` on the server |

Your database password goes in exactly those two places. **If it is in a file
git tracks, rotate it with `mysql:rotate` before you do anything else.**

## Deploying

Two remotes, two different jobs. You need **both**.

| Remote | What it is for |
|---|---|
| `origin` | GitHub. Your code and its history. This is what gets graded |
| `dokku` | The class server. This is what makes the site live |

Your app already exists and its name is on **Deployments**. You only add the
remote — once, and you may well have done it already in **HTML + the
Pipeline**:

```bash
git remote add dokku dokku@iscs2.gcsu.edu:yournetid-6200
```

Then, every time you want the live site to catch up with your edits:

```bash
git add .
git commit -m "Add the routes"
git push origin main    # your code, to GitHub
git push dokku main     # your site, to the class server
```

Pushing to `origin` does **not** update your live site, and pushing to `dokku`
does not save your work to GitHub. Do both, every time.

Visit `/healthz` on your live site to prove the app is up. It also reports
whether your `DATABASE_URL` actually reached the server, which you cannot check
any other way.

If your site is not responding, it may simply be stopped:
`ssh dokku@iscs2.gcsu.edu ps:start yournetid-6200`.

## Using the database (Database + SQL onward)

**Your database already exists.** It was created together with your app and
carries the same name, with dashes turned into underscores. You do not create
it, and you do not name it. Its host, port, name and username are on
**Deployments**; so is its password, and:

```bash
ssh dokku@iscs2.gcsu.edu mysql:url yournetid-6200
```

prints the whole connection string. If the password is unknown, ask for a new
one with `mysql:rotate yournetid-6200` — nothing is lost, and you then update
`DATABASE_URL` in both places below.

```python
from database import get_connection

conn = get_connection()
try:
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM examples WHERE id = %s", (example_id,))
    row = cursor.fetchone()
finally:
    conn.close()
```

Always use `%s` placeholders and pass the values separately. Building a query
by joining strings together is how SQL injection gets in, and it will cost you
marks.

Load `database/schema.sql` first, then `database/seed_data.sql`.

| Variable | What it does | If you leave it unset |
|---|---|---|
| `DATABASE_URL` | Your database connection string | The app runs; pages needing a database explain that there is not one yet |
| `FLASK_SECRET_KEY` | Signs session cookies | The app runs; anyone logged in is logged out on every restart |

Locally these go in `.env`. On the class server:

```bash
ssh dokku@iscs2.gcsu.edu config:set yournetid-6200 DATABASE_URL="mysql://..."
```

> **The host is `172.17.0.1`, not `localhost`.** Your app runs in a container,
> and inside it `localhost` means the container. That also means **the same
> `DATABASE_URL` will not connect from your laptop** — the app starts, and any
> page needing the database fails. That is expected. Test your data-backed
> pages on the live site.

When you build your own features, four things come out: `blueprints/examples.py`,
`templates/examples.html`, the two `examples_bp` lines in `app.py`, and the
Examples link in `templates/base.html`.

## If something goes wrong

| What you see | What it means |
|---|---|
| `ModuleNotFoundError: No module named 'flask'` | The venv is not activated. Look for `(venv)` in your prompt |
| `Address already in use` | An older `python app.py` is still running. `Ctrl-C` it, or close that terminal |
| `jinja2.exceptions.TemplateNotFound` | The filename in `render_template(...)` does not match the file in `templates/` |
| `Permission denied (publickey)` | Your SSH key is not registered yet. See **HTML + the Pipeline**, Lesson 6 |
| `repository ... does not exist` | The app name in your `dokku` remote is wrong — dots instead of dashes, or a name that is not yours. `python check_server.py` will say |
| `Everything up-to-date` but the site is unchanged | You committed nothing. Run `git add .` and `git commit` first |
| Deploy succeeds, site does not respond | `Procfile` misspelled — capital P, no file extension |
| Site does not respond at all | The app may be stopped: `ssh dokku@iscs2.gcsu.edu ps:start yournetid-6200` |
| `Access denied` from MySQL | Wrong password, or it contains `@ / # +` and was not percent-encoded (`@` becomes `%40`) |
| MySQL errors only on your laptop | Expected — `172.17.0.1` exists only on the server. Test on the live site |
| "No database yet" page | Expected before **Database + SQL**. After that, `DATABASE_URL` is not set on the server |
| Anything else | `ssh dokku@iscs2.gcsu.edu logs yournetid-6200` |

When several of these are true at once, start with `python check_server.py` — it
checks the boring things first so you do not debug your code over a typo in a
port number.

## What not to change

`Procfile`, `gunicorn.conf.py` and `runtime.txt` are tuned for the class
server's memory limit and pin the Python version, so a build that works today
still works in December. Changing them is how a deploy stops working for
reasons that are hard to find.

Never commit a `.env` file, and never put a password in a file git tracks.
`.gitignore` already blocks `.env` — leave that line in place.

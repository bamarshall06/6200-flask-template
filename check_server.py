#!/usr/bin/env python3
"""Check my-server.json against the real server.

    python check_server.py              everything below
    python check_server.py --offline    skip the two checks that need the network

Four things get checked, in this order:

  1. Every value in my-server.json is filled in.
  2. The values agree with each other. Most of them are not free choices -
     your app name comes from your netid, your database name comes from your
     app name - so a typo in one shows up as a disagreement with another.
  3. Your git remotes point where this file says they do.
  4. Your live site answers, and your .env agrees with this file.

It only ever reads. It never changes your project, your database or your
server, so it is safe to run as often as you like.

Nothing here is magic you will need later - it is a few string comparisons and
one web request. Read it if you are curious.
"""

import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request

HOST = "iscs2.gcsu.edu"
DB_HOST = "172.17.0.1"
DB_PORT = 3306
TIMEOUT = 15

# Filled in as we go: (ok, label, detail)
results = []


def check(ok, label, detail=""):
    results.append((ok, label, detail))


def load():
    """Read my-server.json, or explain exactly what is wrong with it."""
    try:
        with open("my-server.json", encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        sys.exit(
            "my-server.json is not here.\n"
            "Run this from the top of your project, the folder holding app.py."
        )
    except json.JSONDecodeError as exc:
        sys.exit(
            "my-server.json is not valid JSON: {0}\n"
            "Line {1}. Usually a missing comma, or a trailing one after the "
            "last entry.".format(exc.msg, exc.lineno)
        )


# --- 1. is it filled in ------------------------------------------------------

def check_filled(cfg):
    wanted = ["netid", "app_name", "live_url", "port", "github_repo",
              "dokku_remote"]
    missing = [k for k in wanted if not cfg.get(k)]
    db = cfg.get("database") or {}
    missing += ["database." + k for k in ("name", "username", "host", "port")
                if not db.get(k)]

    if missing:
        check(False, "my-server.json is filled in",
              "still empty: " + ", ".join(missing))
    else:
        check(True, "my-server.json is filled in")
    return not missing


# --- 2. do the values agree with each other ----------------------------------

def check_consistent(cfg):
    netid = cfg["netid"].strip()
    app = cfg["app_name"].strip()
    port = cfg["port"]
    db = cfg["database"]

    if "@" in netid:
        check(False, "netid is a netid, not an email",
              "{0} - use just the part before the @".format(netid))
        netid = netid.split("@")[0]
    else:
        check(True, "netid is a netid, not an email")

    # Everything below is derived from the netid, NOT from whatever app_name
    # happens to say. If app_name is the thing that is wrong, deriving the
    # database name and the remote from it would make every other line point at
    # a second wrong answer - which is how a student ends up "fixing" four
    # fields to match one typo.
    expected_app = netid.replace(".", "-") + "-6200"
    check(app == expected_app, "app name matches your netid",
          "" if app == expected_app else
          "this file says {0}, your netid gives {1}".format(app, expected_app))

    expected_url = "https://{0}:{1}".format(HOST, port)
    url = cfg["live_url"].strip().rstrip("/")
    check(url == expected_url, "live URL matches your port",
          "" if url == expected_url else
          "this file says {0}, your port gives {1}".format(url, expected_url))

    expected_remote = "dokku@{0}:{1}".format(HOST, expected_app)
    remote = cfg["dokku_remote"].strip()
    check(remote == expected_remote, "dokku remote matches your app name",
          "" if remote == expected_remote else
          "this file says {0}, should be {1}".format(remote, expected_remote))

    expected_db = expected_app.replace("-", "_")
    check(db["name"] == expected_db, "database name matches your app name",
          "" if db["name"] == expected_db else
          "this file says {0}, your app name gives {1}".format(
              db["name"], expected_db))

    check(db["username"] == db["name"],
          "database username matches the database name",
          "" if db["username"] == db["name"] else
          "username {0}, database {1} - for us they are always the same "
          "string".format(db["username"], db["name"]))

    check(db["host"] == DB_HOST and int(db["port"]) == DB_PORT,
          "database host and port are the ones inside the container",
          "" if db["host"] == DB_HOST and int(db["port"]) == DB_PORT else
          "expected {0}:{1}, not localhost - your app runs in a container, "
          "and inside it localhost means the container".format(DB_HOST, DB_PORT))


# --- the password must not be in here ----------------------------------------

def check_no_secrets(cfg):
    """The one check that matters more than all the others.

    A password in a tracked file is the mistake this course warns about most,
    and it is worth catching here rather than in a code review after the fact.
    Automated scanners read public GitHub within hours of a push.
    """
    blob = json.dumps(cfg).lower()
    smells = [w for w in ("password", "passwd", "secret", "database_url", "mysql://")
              if w in blob]
    # The _comment block legitimately uses these words to tell you not to do it.
    stripped = {k: v for k, v in cfg.items() if not k.startswith("_")}
    stripped.pop("database", None)
    real = json.dumps(stripped).lower()
    real_smells = [w for w in smells if w in real
                   or w in json.dumps(cfg.get("database", {})).lower()]

    if real_smells:
        check(False, "no password or connection string in this file",
              "found {0} - take it out, rotate it with "
              "'ssh dokku@{1} mysql:rotate <app>', and put the new one in "
              ".env and config:set only".format(", ".join(real_smells), HOST))
    else:
        check(True, "no password or connection string in this file")


# --- 3. git remotes ----------------------------------------------------------

def check_remotes(cfg):
    try:
        out = subprocess.run(["git", "remote", "-v"], capture_output=True,
                             text=True, timeout=10).stdout
    except (OSError, subprocess.SubprocessError) as exc:
        check(False, "git remotes are set", "could not run git: {0}".format(exc))
        return

    if not out.strip():
        check(False, "git remotes are set",
              "this project has no remotes at all - see HTML + the Pipeline, "
              "Lesson 7")
        return

    check(cfg["dokku_remote"] in out, "dokku remote is added",
          "" if cfg["dokku_remote"] in out else
          "add it with: git remote add dokku " + cfg["dokku_remote"])

    repo = cfg["github_repo"].strip().rstrip("/")
    slug = repo.replace("https://github.com/", "").replace(".git", "")
    check(bool(slug) and slug in out.replace(".git", ""),
          "origin is the GitHub repo named in this file",
          "" if slug in out.replace(".git", "") else
          "git says origin is something else - check github_repo")


# --- 4. the live site, and .env ---------------------------------------------

def check_live(cfg):
    url = cfg["live_url"].strip().rstrip("/") + "/healthz"
    try:
        with urllib.request.urlopen(url, timeout=TIMEOUT) as resp:
            body = resp.read(2000).decode("utf-8", "replace")
            code = resp.status
    except urllib.error.HTTPError as exc:
        check(False, "live site answers on /healthz",
              "{0} returned HTTP {1}. The app is deployed but erroring - "
              "'ssh dokku@{2} logs {3}'".format(
                  url, exc.code, HOST, cfg["app_name"]))
        return
    except (urllib.error.URLError, OSError) as exc:
        check(False, "live site answers on /healthz",
              "could not reach {0}: {1}. Either the app is stopped "
              "('ssh dokku@{2} ps:start {3}') or you are off the network."
              .format(url, getattr(exc, "reason", exc), HOST, cfg["app_name"]))
        return

    check(code == 200, "live site answers on /healthz",
          "" if code == 200 else "HTTP {0}".format(code))

    # /healthz answers {"status": "ok", "database": true|false}, where database
    # is whether DATABASE_URL actually reached the server. It is the only way to
    # check that - students are not allowed to run config:show.
    try:
        health = json.loads(body)
    except json.JSONDecodeError:
        check(False, "live site's /healthz returns JSON",
              "got something else - is this app running this kit's app.py?")
        return

    if health.get("database"):
        check(True, "live site has its DATABASE_URL set")
    else:
        check(True, "live site has no DATABASE_URL yet",
              "expected until Database + SQL; after that, set it with "
              "'ssh dokku@{0} config:set {1} DATABASE_URL=...'".format(
                  HOST, cfg["app_name"]))


def check_env(cfg):
    """Does .env agree with this file? The password is never printed."""
    if not os.path.exists(".env"):
        check(True, ".env",
              "not present - expected until Database + SQL")
        return

    url = None
    with open(".env", encoding="utf-8") as fh:
        for line in fh:
            if line.strip().startswith("DATABASE_URL="):
                url = line.split("=", 1)[1].strip().strip("'\"")

    if not url:
        check(True, ".env has no DATABASE_URL yet",
              "expected until Database + SQL")
        return

    # mysql://user:password@host:port/dbname - we look at everything but the password.
    m = re.match(r"mysql://([^:]+):([^@]*)@([^:/]+):(\d+)/(\S+)", url)
    if not m:
        check(False, "DATABASE_URL in .env is shaped correctly",
              "expected mysql://user:password@host:3306/dbname")
        return

    user, _password, host, port, name = m.groups()
    db = cfg["database"]
    problems = []
    if user != db["username"]:
        problems.append("username is {0}, this file says {1}".format(
            user, db["username"]))
    if name != db["name"]:
        problems.append("database is {0}, this file says {1}".format(
            name, db["name"]))
    if host != db["host"]:
        problems.append("host is {0}, this file says {1}".format(
            host, db["host"]))
    if int(port) != int(db["port"]):
        problems.append("port is {0}, this file says {1}".format(
            port, db["port"]))

    check(not problems, ".env agrees with this file", "; ".join(problems))

    if url != url.strip() or " " in url:
        check(False, "DATABASE_URL has no stray spaces",
              "there is a space in it - that breaks the connection in a way "
              "that reads like the database being down")


# --- output -----------------------------------------------------------------

def main():
    offline = "--offline" in sys.argv
    cfg = load()

    complete = check_filled(cfg)
    check_no_secrets(cfg)
    if complete:
        check_consistent(cfg)
        check_remotes(cfg)
        check_env(cfg)       # reads a local file; no network needed
        if not offline:
            check_live(cfg)  # the only check that goes out to the server

    width = max(len(label) for _, label, _ in results)
    print()
    for ok, label, detail in results:
        mark = "ok  " if ok else "FAIL"
        print("  {0}  {1}  {2}".format(mark, label.ljust(width), detail))
    print()

    failed = [label for ok, label, _ in results if not ok]
    if not complete:
        print("  Fill in my-server.json from the Deployments page in the "
              "course sidebar,\n  then run this again.\n")
        return 1
    if failed:
        print("  {0} to fix. Each FAIL line says what, and how.\n".format(
            "1 thing" if len(failed) == 1 else "{0} things".format(len(failed))))
        return 1
    print("  Everything agrees.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Talking to the class MySQL server.

Two things here are worth reading before you change them.

**The database is optional.** `is_configured()` is how the app knows whether a
connection string exists. Flask + Routes has no database and does not need one -
the site runs fine without it, and the Examples page politely says so.
Database + SQL is when you connect the one you already have.

**A failure raises.** It does not return None and it does not print a warning
and carry on. A connection that quietly fails looks exactly like a table with no
rows in it, and you will spend an hour on the query before you think to check
the password.
"""

import os
from urllib.parse import unquote, urlparse

import mysql.connector


class DatabaseNotConfigured(RuntimeError):
    """No DATABASE_URL is set, or it is not usable.

    app.py turns this into a friendly 503 page rather than a crash, so a site
    with no database still works everywhere except the pages that need one.
    """


# DATABASE_URL is the name this course uses. JAWSDB_URL is read as a fallback so
# a project carried over from an older semester keeps working without edits.
URL_ENV_VARS = ("DATABASE_URL", "JAWSDB_URL")


def _connection_url():
    for name in URL_ENV_VARS:
        value = os.getenv(name)
        if value:
            return value
    return None


def is_configured():
    """True when a connection string is present. Does not connect to anything."""
    return _connection_url() is not None


def get_connection():
    """Open a NEW connection to the class MySQL server.

    Every call opens its own connection, and whoever called it is responsible
    for closing it:

        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM examples")
            rows = cursor.fetchall()
        finally:
            conn.close()

    Never returns None. If something is wrong you get an exception that says
    what is wrong, rather than a query that silently returns nothing.
    """
    url = _connection_url()
    if not url:
        raise DatabaseNotConfigured(
            "No DATABASE_URL is set. Put one in .env for local work, or set it "
            "on the class server with: ssh dokku@iscs2.gcsu.edu config:set "
            "<your-app> DATABASE_URL=mysql://user:password@host:3306/dbname"
        )

    parts = urlparse(url)
    database = parts.path.lstrip("/")
    if not parts.hostname or not database:
        raise DatabaseNotConfigured(
            f"DATABASE_URL is not a usable connection string: {url!r}. Expected "
            "mysql://username:password@host:3306/database_name"
        )

    # unquote() matters: database passwords often contain @ / # or +, which have
    # to be percent-encoded inside a URL. Without this you get a bare
    # "Access denied" and no hint that the password was the problem.
    return mysql.connector.connect(
        host=parts.hostname,
        user=unquote(parts.username or ""),
        password=unquote(parts.password or ""),
        database=database,
        port=parts.port or 3306,
        connection_timeout=5,
    )

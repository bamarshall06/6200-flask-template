"""A working example of Create, Read, Update and Delete over one table.

This is the file you will copy. In Database + SQL you tell Claude Code to build your
own blueprint "based on the examples.py blueprint formatting" - so the shape
here is the shape you want repeated, which is why every query is written out in
full instead of being hidden behind helper functions.

When you no longer need it, four things come out:
  1. this file
  2. templates/examples.html
  3. the import and register_blueprint lines in app.py
  4. the Examples link in templates/base.html
"""

from flask import Blueprint, flash, redirect, render_template, request, url_for

from database import get_connection

examples_bp = Blueprint("examples", __name__)


@examples_bp.route("/examples")
def examples():
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, name, description, created_at "
            "FROM examples ORDER BY created_at DESC"
        )
        rows = cursor.fetchall()
    finally:
        # Always in a finally block. Every request opens its own connection, so
        # one that is never closed stays open on a server the whole class
        # shares.
        conn.close()
    return render_template("examples.html", examples=rows)


@examples_bp.route("/examples/add", methods=["POST"])
def add_example():
    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()

    if not name:
        flash("Name is required.", "danger")
        return redirect(url_for("examples.examples"))

    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        # %s is the placeholder. Never build SQL by joining strings together or
        # with an f-string - that is how SQL injection gets in.
        cursor.execute(
            "INSERT INTO examples (name, description) VALUES (%s, %s)",
            (name, description),
        )
        conn.commit()
    finally:
        conn.close()

    flash(f"Added {name}.", "success")
    return redirect(url_for("examples.examples"))


@examples_bp.route("/examples/edit/<int:example_id>", methods=["POST"])
def edit_example(example_id):
    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()

    if not name:
        flash("Name is required.", "danger")
        return redirect(url_for("examples.examples"))

    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "UPDATE examples SET name = %s, description = %s WHERE id = %s",
            (name, description, example_id),
        )
        conn.commit()
    finally:
        conn.close()

    flash(f"Updated {name}.", "success")
    return redirect(url_for("examples.examples"))


@examples_bp.route("/examples/delete/<int:example_id>", methods=["POST"])
def delete_example(example_id):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("DELETE FROM examples WHERE id = %s", (example_id,))
        conn.commit()
    finally:
        conn.close()

    flash("Deleted.", "success")
    return redirect(url_for("examples.examples"))

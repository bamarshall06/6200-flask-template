"""Gunicorn settings, sized for the class server rather than for your laptop.

Gunicorn picks this file up automatically when it starts, which is why the
Procfile is just `web: gunicorn app:app` with nothing after it.

Your app runs in a container with 256 MB of memory and half of one CPU. These
numbers are chosen for that. You should not need to change them.
"""

# One worker process. Half a CPU cannot usefully run two, and a second one
# competes with the first for memory.
workers = 1

# Concurrency comes from threads instead. Once your pages start calling
# other people's APIs and waiting on them; without threads, one slow call blocks
# everybody else's page load. Threads cost almost nothing in memory.
threads = 4

# Give up on a request after 30 seconds rather than holding the worker forever.
timeout = 30

# Restart the worker every so often. If a page ever forgets to close its
# database connection, this stops the leak growing without bound. The jitter
# keeps restarts from all landing at once.
max_requests = 250
max_requests_jitter = 50

# Log every request. Gunicorn does not do this by default, which is why a
# deployed app can look silent in `dokku logs` when a page is 404ing.
accesslog = "-"
errorlog = "-"

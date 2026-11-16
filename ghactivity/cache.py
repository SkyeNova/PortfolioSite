"""In-memory + atomic on-disk cache with stale-while-revalidate.

Each Resource keeps its last good copy forever and refreshes in a background
thread (one at a time, with a lock). `get()` never blocks on a fresh fetch
unless there is nothing at all to serve, and then only for `cold_wait` seconds.
Failures keep the stale copy and back off for a minute.
"""
import json
import logging
import os
import threading
import time

from .config import CACHE_DIR

log = logging.getLogger("ghactivity")

RETRY_AFTER = 60


class Resource:
    def __init__(self, name, fetch, ttl, cache_dir=CACHE_DIR):
        self.name = name
        self._fetch = fetch
        self._ttl = ttl if isinstance(ttl, dict) else {"token": ttl, "public": ttl}
        self._dir = cache_dir
        self._lock = threading.Lock()
        self._idle = threading.Event()
        self._idle.set()
        self._mem = None
        self._disk_read_at = 0.0
        self._last_failure = 0.0
        self.last_error = None

    # ---------- storage ----------

    @property
    def path(self):
        return self._dir / f"gh_{self.name}.json"

    def _read_disk(self):
        try:
            with open(self.path, encoding="utf-8") as f:
                entry = json.load(f)
        except (OSError, ValueError):
            return None
        if not isinstance(entry, dict) or "data" not in entry or "fetched_at" not in entry:
            return None
        return entry

    def _write_disk(self, entry):
        try:
            self._dir.mkdir(parents=True, exist_ok=True)
            tmp = self.path.with_suffix(".json.tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(entry, f, separators=(",", ":"))
            os.replace(tmp, self.path)
        except OSError as e:
            log.warning("ghactivity: could not write cache %s (%s)", self.name, type(e).__name__)

    def peek(self):
        """Best copy we have, without fetching. Re-reads disk when memory is old."""
        now = time.time()
        with self._lock:
            entry = self._mem
            fresh = entry is not None and self.is_fresh(entry, entry.get("mode"), now)
            if not fresh and now - self._disk_read_at > 5:
                self._disk_read_at = now
                disk = self._read_disk()
                if disk and (entry is None or disk["fetched_at"] > entry["fetched_at"]):
                    self._mem = entry = disk
            return entry

    # ---------- freshness ----------

    def ttl_for(self, mode):
        return self._ttl.get(mode, self._ttl.get("public", 1800))

    def is_fresh(self, entry, mode, now=None):
        now = now or time.time()
        return entry.get("mode") == mode and now - float(entry.get("fetched_at", 0)) < self.ttl_for(mode)

    def age(self, entry):
        return time.time() - float(entry.get("fetched_at", 0))

    # ---------- fetching ----------

    def refresh(self, mode):
        """Start a background refresh unless one is running or we failed very recently."""
        with self._lock:
            if not self._idle.is_set():
                return False
            if time.time() - self._last_failure < RETRY_AFTER:
                return False
            self._idle.clear()
        threading.Thread(target=self._run, args=(mode,), name=f"gh-{self.name}", daemon=True).start()
        return True

    def _run(self, mode):
        try:
            data = self._fetch(mode)
            entry = {"fetched_at": time.time(), "mode": mode, "data": data}
            with self._lock:
                self._mem = entry
                self.last_error = None
            self._write_disk(entry)
            log.info("ghactivity: refreshed %s (%s)", self.name, mode)
        except Exception as e:  # keep serving the last good copy
            self._last_failure = time.time()
            self.last_error = f"{type(e).__name__}: {e}"
            log.warning("ghactivity: %s refresh failed: %s", self.name, self.last_error)
        finally:
            self._idle.set()

    def wait(self, seconds):
        self._idle.wait(seconds)

    def get(self, mode, cold_wait=0.0):
        """Fresh copy, else stale copy (refreshing in the background), else None."""
        entry = self.peek()
        if entry and self.is_fresh(entry, mode):
            return entry
        self.refresh(mode)
        if entry:
            return entry
        if cold_wait > 0:
            self.wait(cold_wait)
            entry = self.peek()
        return entry

    def clear_memory(self):
        with self._lock:
            self._mem = None
            self._disk_read_at = 0.0

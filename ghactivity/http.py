"""Thin urllib wrappers. 8 s timeout, one user agent, no token in any error text."""
import json
import logging
import urllib.error
import urllib.request

log = logging.getLogger("ghactivity")

TIMEOUT = 8
USER_AGENT = "skyenova.dev (ghactivity; +https://skyenova.dev)"
API = "https://api.github.com"
GRAPHQL = "https://api.github.com/graphql"


class FetchError(Exception):
    """Anything that stops a fetch. Messages never include request headers."""


def _request(url, data=None, headers=None, timeout=TIMEOUT):
    req = urllib.request.Request(url, data=data, method="POST" if data else "GET")
    req.add_header("User-Agent", USER_AGENT)
    req.add_header("Accept", "application/json" if "api.github.com" in url else "text/html")
    for key, value in (headers or {}).items():
        req.add_header(key, value)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except urllib.error.HTTPError as e:
        raise FetchError(f"HTTP {e.code} for {url.split('?')[0]}") from None
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        raise FetchError(f"{type(e).__name__} for {url.split('?')[0]}") from None


def get_text(url, timeout=TIMEOUT):
    return _request(url, timeout=timeout).decode("utf-8", "replace")


def get_json(url, token=None, timeout=TIMEOUT):
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        return json.loads(_request(url, headers=headers, timeout=timeout))
    except ValueError:
        raise FetchError(f"bad JSON from {url.split('?')[0]}") from None


def graphql(query, variables, token, timeout=TIMEOUT):
    if not token:
        raise FetchError("GraphQL needs a token")
    body = json.dumps({"query": query, "variables": variables}).encode()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    try:
        payload = json.loads(_request(GRAPHQL, data=body, headers=headers, timeout=timeout))
    except ValueError:
        raise FetchError("bad JSON from GraphQL") from None
    if payload.get("errors") and not payload.get("data"):
        kinds = sorted({str(e.get("type", "ERROR")) for e in payload["errors"]})
        raise FetchError("GraphQL errors: " + ", ".join(kinds))
    if payload.get("errors"):
        log.warning("ghactivity: GraphQL returned partial data (%d errors)", len(payload["errors"]))
    rate = (payload.get("data") or {}).get("rateLimit")
    if rate:
        log.debug("ghactivity: GraphQL cost %s, %s remaining", rate.get("cost"), rate.get("remaining"))
    return payload["data"]

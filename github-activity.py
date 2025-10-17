import argparse
import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from datetime import datetime
import sys
import os
from typing import Optional, List

HTTP_API_URL = "https://api.github.com/users/{username}/events"

# ==========================
# JSON File Events Storage
# ==========================
EVENTS_FILE = 'events.json'


def load_events() -> List[dict]:
    if os.path.exists(EVENTS_FILE):
        try:
            with open(EVENTS_FILE, 'r', encoding='utf-8') as file:
                return json.load(file)
        except (OSError, json.JSONDecodeError):
            return []
    return []


def save_events(events: List[dict]) -> None:
    with open(EVENTS_FILE, 'w', encoding='utf-8') as file:
        json.dump(events, file, indent=2, ensure_ascii=False)


def generate_id(events: List[dict]) -> int:
    if events:
        return max(event.get('id', 0) for event in events) + 1
    return 1


# ==========================
# GitHub Activity Functions
# ==========================
def fetch_github_events(username: str, limit: int = 10, token: Optional[str] = None) -> Optional[List[dict]]:
    url = HTTP_API_URL.format(username=username)
    headers = {'User-Agent': 'github-activity-tracker'}
    if token:
        headers['Authorization'] = f'token {token}'
    req = Request(url, headers=headers)
    try:
        with urlopen(req, timeout=10) as response:
            status = getattr(response, 'status', None) or response.getcode()
            if status == 200:
                data = json.load(response)
                if isinstance(data, list):
                    return data[:limit]
                return data
            else:
                raise ValueError(f"Error fetching events: {status}")
    except HTTPError as e:
        if e.code == 404:
            raise ValueError(f"User {username} not found.")
        elif e.code == 403:
            raise RuntimeError("API rate limit exceeded or access forbidden (403). Try authenticating with a token.")
        else:
            raise RuntimeError(f"HTTP error occurred: {e.code} {e.reason}")
    except URLError as e:
        raise RuntimeError(f"Failed to reach the server: {e.reason}")
    except json.JSONDecodeError:
        raise RuntimeError("Failed to parse JSON response.")
    return None


def _truncate(text: Optional[str], max_length: int) -> str:
    if not text:
        return ''
    s = str(text)
    if len(s) > max_length:
        return s[:max_length-3] + '...'
    return s


def format_event(event: dict, max_length: int = 80) -> str:
    t = event.get('type', 'UnknownEvent')
    repo = event.get('repo', {}).get('name', 'UnknownRepo')
    payload = event.get('payload', {})

    if t == 'PushEvent':
        commits = payload.get('commits', [])
        cnt = len(commits)
        return f"Pushed {cnt} commit{'s' if cnt != 1 else ''} to {repo}"

    if t == 'IssuesEvent':
        action = payload.get('action') or 'performed'
        issue = _truncate(payload.get('issue', {}).get('title'), max_length)
        return f"{action.capitalize()} issue '{issue}' in {repo}"

    if t == 'WatchEvent':
        action = payload.get('action', 'started')
        return f"{action.capitalize()} watching {repo}"

    if t == 'IssueCommentEvent':
        action = payload.get('action') or 'commented'
        issue = _truncate(payload.get('issue', {}).get('title'), max_length)
        return f"{action.capitalize()} comment on issue '{issue}' in {repo}"

    if t == 'PullRequestEvent':
        action = payload.get('action') or 'performed'
        pr = _truncate(payload.get('pull_request', {}).get('title'), max_length)
        return f"{action.capitalize()} pull request '{pr}' in {repo}"

    if t == 'PullRequestReviewCommentEvent':
        return f"Commented on a pull request in {repo}"

    if t == 'CreateEvent':
        ref_type = payload.get('ref_type') or 'ref'
        ref = payload.get('ref') or ''
        return f"Created {ref_type} '{ref}' in {repo}"

    if t == 'DeleteEvent':
        ref_type = payload.get('ref_type') or 'ref'
        ref = payload.get('ref') or ''
        return f"Deleted {ref_type} '{ref}' in {repo}"

    if t == 'ForkEvent':
        forkee = payload.get('forkee', {}).get('full_name') or '<fork>'
        return f"Forked {repo} to {forkee}"

    if t == 'ReleaseEvent':
        action = payload.get('action') or 'released'
        release = payload.get('release', {}).get('tag_name') or ''
        return f"{action.capitalize()} release '{release}' in {repo}"

    if t == 'StarEvent' or t == 'WatchEvent':
        action = payload.get('action') or 'starred'
        return f"{action.capitalize()} {repo}"

    # fallback
    return f"{t} on {repo}"


def print_events(events: Optional[List[dict]], limit: int = 10) -> None:
    if not events:
        print("No events found.")
        return
    for idx, ev in enumerate(events[:limit], start=1):
        desc = format_event(ev)
        created = ev.get('created_at')
        if created:
            try:
                ts = created.rstrip('Z')
                when = datetime.fromisoformat(ts).strftime('%Y-%m-%d %H:%M')
            except Exception:
                when = created
            print(f"- {desc} ({when})")
        else:
            print(f"- {desc}")


def main():
    parser = argparse.ArgumentParser(description="GitHub User Activity Tracker")
    subparsers = parser.add_subparsers(dest='command', required=True)
    fetch_parser = subparsers.add_parser('fetch', help='Fetch GitHub user activity')
    fetch_parser.add_argument('username', help='GitHub username to fetch activity for')
    fetch_parser.add_argument('--limit', '-n', type=int, default=10, help="Number of events to fetch (default: 10)")

    args = parser.parse_args()

    if args.command == 'fetch':
        token = os.environ.get('GITHUB_TOKEN')
        try:
            events = fetch_github_events(args.username, args.limit, token=token)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(2)
        except RuntimeError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(3)

        print_events(events, limit=args.limit)

        if not events:
            print("No events to display.")
            return

        try:
            save_events(events)
            print(f"Saved {len(events)} events to {EVENTS_FILE}")
        except Exception as e:
            print(f"Warning: failed to write JSON file: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
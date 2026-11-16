"""Pure functions over daily counts and commit timestamps. No I/O, no Flask."""
from collections import Counter
from datetime import date, datetime, timedelta, timezone

WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
WEEKDAYS_FULL = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def parse_date(value):
    return date.fromisoformat(str(value)[:10])


def parse_datetime(value):
    """ISO 8601 with Z or offset -> aware datetime (UTC if naive)."""
    text = str(value).replace("Z", "+00:00")
    dt = datetime.fromisoformat(text)
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def days_from_years(years):
    """{"2025": {"days": [["2025-01-01", 3], ...]}} -> {date: count}."""
    days = {}
    for block in (years or {}).values():
        for item in block.get("days", []):
            try:
                days[parse_date(item[0])] = max(0, int(item[1]))
            except (ValueError, TypeError, IndexError):
                continue
    return days


# ---------- headline numbers ----------

def streaks(days, today):
    """Current streak counts from yesterday if today is still 0."""
    start = today if days.get(today, 0) > 0 else today - timedelta(days=1)
    current = 0
    d = start
    while days.get(d, 0) > 0:
        current += 1
        d -= timedelta(days=1)

    longest, run, best_end = 0, 0, None
    if days:
        d, last = min(days), max(min(max(days), today), min(days))
        while d <= last:
            if days.get(d, 0) > 0:
                run += 1
                if run > longest:
                    longest, best_end = run, d
            else:
                run = 0
            d += timedelta(days=1)
    best_start = best_end - timedelta(days=longest - 1) if best_end else None
    return {"current": current, "longest": longest, "longest_start": best_start, "longest_end": best_end}


def this_week(days, today):
    monday = today - timedelta(days=today.weekday())
    return sum(days.get(monday + timedelta(days=i), 0) for i in range((today - monday).days + 1))


def last_active(days, today):
    past = [d for d, c in days.items() if c > 0 and d <= today]
    return max(past) if past else None


def busiest(days, year):
    best = None
    for d, c in days.items():
        if d.year == year and c > 0 and (best is None or c > best[1] or (c == best[1] and d < best[0])):
            best = (d, c)
    return {"date": best[0], "count": best[1]} if best else None


def totals_by_year(days):
    totals = Counter()
    for d, c in days.items():
        totals[d.year] += c
    return dict(totals)


def in_range(days, start, end):
    return sum(c for d, c in days.items() if start <= d <= end)


# ---------- heatmap ----------

def level_scale(counts):
    """Count -> 0..4 using quartiles of the non-zero days, so pink stays rare."""
    nonzero = sorted(c for c in counts if c > 0)
    if not nonzero:
        return lambda c: 0
    n = len(nonzero)

    def q(p):
        return nonzero[min(n - 1, int(p * n))]

    q1, q2, q3 = q(0.25), q(0.5), q(0.75)

    def level(c):
        if c <= 0:
            return 0
        if c <= q1:
            return 1
        if c <= q2:
            return 2
        if c <= q3:
            return 3
        return 4

    return level


def day_label(d, count):
    when = f"{WEEKDAYS[d.weekday()]} {d.day} {MONTHS[d.month - 1]} {d.year}"
    if count == 0:
        return f"No contributions on {when}"
    return f"{count} contribution{'s' if count != 1 else ''} on {when}"


def year_grid(days, year, today):
    """Monday-first week columns covering the whole year, plus month spans."""
    first, last = date(year, 1, 1), date(year, 12, 31)
    start = first - timedelta(days=first.weekday())
    end = last + timedelta(days=6 - last.weekday())
    level = level_scale([c for d, c in days.items() if d.year == year])

    weeks, months = [], []
    d = start
    while d <= end:
        column = []
        month_of_column = None
        for _ in range(7):
            in_year = d.year == year
            future = d > today
            count = days.get(d, 0) if in_year and not future else 0
            if in_year and month_of_column is None:
                month_of_column = d.month
            column.append({
                "date": d.isoformat(),
                "count": count,
                "level": level(count) if in_year and not future else 0,
                "in_year": in_year,
                "future": in_year and future,
                "label": day_label(d, count) if in_year and not future else "",
            })
            d += timedelta(days=1)
        weeks.append(column)
        if months and months[-1]["month"] == month_of_column:
            months[-1]["span"] += 1
        else:
            months.append({"month": month_of_column, "label": MONTHS[month_of_column - 1], "span": 1})

    total = sum(c for d, c in days.items() if d.year == year and d <= today)
    return {"year": year, "weeks": weeks, "months": months, "total": total}


def mini_grid(days, today, weeks=20):
    """The last N weeks as Monday-first columns, for the homepage card."""
    end = today + timedelta(days=6 - today.weekday())
    start = end - timedelta(days=weeks * 7 - 1)
    level = level_scale([c for d, c in days.items() if start <= d <= today])
    columns, d = [], start
    while d <= end:
        column = []
        for _ in range(7):
            future = d > today
            count = 0 if future else days.get(d, 0)
            column.append({"level": 0 if future else level(count), "future": future})
            d += timedelta(days=1)
        columns.append(column)
    return columns


# ---------- rhythm ----------

def weekday_counts(days, today, span_days=365):
    start = today - timedelta(days=span_days - 1)
    counts = [0] * 7
    for d, c in days.items():
        if start <= d <= today:
            counts[d.weekday()] += c
    return counts


def punch_card(timestamps, tz):
    """Aware datetimes -> 7x24 grid of counts in the given zone."""
    grid = [[0] * 24 for _ in range(7)]
    for ts in timestamps:
        local = ts.astimezone(tz)
        grid[local.weekday()][local.hour] += 1
    return grid


_BUCKETS = [
    ("at night", range(0, 6)),
    ("in the mornings", range(6, 12)),
    ("in the afternoons", range(12, 18)),
    ("in the evenings", range(18, 24)),
]


def rhythm_caption_hours(grid):
    total = sum(map(sum, grid))
    if total < 10:
        return "Not enough commits in the last few months to say much."
    by_hour = [sum(row[h] for row in grid) for h in range(24)]
    name, _ = max(_BUCKETS, key=lambda b: sum(by_hour[h] for h in b[1]))
    by_day = [sum(row) for row in grid]
    weekend = by_day[5] + by_day[6]
    sentence = f"Mostly {name}."
    if weekend / total >= 0.45:
        sentence += " A lot of it at the weekend."
    else:
        top = max(range(7), key=lambda i: by_day[i])
        if by_day[top] / total >= 0.22:
            sentence += f" {WEEKDAYS_FULL[top]}s are the busiest."
    return sentence


def rhythm_caption_weekdays(counts):
    total = sum(counts)
    if total == 0:
        return "Nothing in the last year."
    top = max(range(7), key=lambda i: counts[i])
    low = min(range(7), key=lambda i: counts[i])
    if counts[top] == counts[low]:
        return "Spread evenly across the week."
    return f"Busiest on {WEEKDAYS_FULL[top]}s, quietest on {WEEKDAYS_FULL[low]}s."


# ---------- relative wording ----------

def relative_day(d, today):
    if d is None:
        return "never"
    delta = (today - d).days
    if delta <= 0:
        return "today"
    if delta == 1:
        return "yesterday"
    if delta < 7:
        return f"{delta} days ago"
    if delta < 35:
        weeks = delta // 7
        return f"{weeks} week{'s' if weeks != 1 else ''} ago"
    if d.year == today.year:
        return f"on {d.day} {MONTHS[d.month - 1]}"
    return f"on {d.day} {MONTHS[d.month - 1]} {d.year}"


def relative_time(dt, now):
    """Compact form for commit rows."""
    local = dt.astimezone(now.tzinfo)
    seconds = (now - local).total_seconds()
    if seconds < 3600:
        return "just now"
    if local.date() == now.date():
        return f"{int(seconds // 3600)} h ago"
    days = (now.date() - local.date()).days
    if days == 1:
        return "yesterday"
    if days < 7:
        return f"{days} days ago"
    if days < 35:
        weeks = days // 7
        return f"{weeks} wk ago" if weeks == 1 else f"{weeks} wks ago"
    if local.year == now.year:
        return f"{local.day} {MONTHS[local.month - 1]}"
    return f"{MONTHS[local.month - 1]} {local.year}"


def date_range_label(start, end):
    if not start or not end:
        return ""
    if start == end:
        return f"{start.day} {MONTHS[start.month - 1]} {start.year}"
    if start.year == end.year:
        if start.month == end.month:
            return f"{start.day}–{end.day} {MONTHS[start.month - 1]} {start.year}"
        return f"{start.day} {MONTHS[start.month - 1]} – {end.day} {MONTHS[end.month - 1]} {start.year}"
    return f"{MONTHS[start.month - 1]} {start.year} – {MONTHS[end.month - 1]} {end.year}"

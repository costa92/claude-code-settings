#!/usr/bin/env python3
"""
AI Daily News Fetcher
Fetches AI news from multiple RSS sources and returns structured data.

Supported sources:
- smol.ai: Daily AI news digest
- Import AI: Jack Clark's weekly AI newsletter
- Last Week in AI: Weekly AI news summary
- Ahead of AI: Sebastian Raschka's ML/AI research updates
- TLDR AI: Daily AI newsletter
"""
import sys
import json
import argparse
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import feedparser
    import requests
except ImportError:
    print("Error: Required packages not installed.")
    print("Run: pip install feedparser requests")
    sys.exit(1)

REQUEST_TIMEOUT = 30

# Content truncation settings (to avoid exceeding 256KB limit)
MAX_CONTENT_LENGTH = 50000  # Maximum characters per entry content
DEFAULT_LIMIT_ALL_SOURCES = 3  # Default limit when using --all-sources
OUTPUT_DIR = Path.home() / ".claude" / "skills" / "news-daily" / "data"  # Default output directory

# How many hours old a digest can be before we consider it "stale" and supplement with realtime sources
STALE_THRESHOLD_HOURS = 36

# RSS Sources Configuration
RSS_SOURCES = {
    # === Daily Sources (English) ===
    "smol": {
        "name": "smol.ai",
        "url": "https://news.smol.ai/rss.xml",
        "description": "Daily AI news digest curated by smol.ai",
        "frequency": "daily",
        "language": "en",
    },
    "tldrai": {
        "name": "TLDR Tech",
        "url": "https://tldr.tech/rss",
        "description": "Daily tech newsletter covering AI, startups, and dev news",
        "frequency": "daily",
        "language": "en",
    },

    # === Weekly Sources (English) ===
    "importai": {
        "name": "Import AI",
        "url": "https://importai.substack.com/feed",
        "description": "Jack Clark's weekly AI newsletter covering research, policy, and industry",
        "frequency": "weekly",
        "language": "en",
    },
    "lastweekinai": {
        "name": "Last Week in AI",
        "url": "https://lastweekin.ai/feed",
        "description": "Weekly text and audio summaries of AI news",
        "frequency": "weekly",
        "language": "en",
    },
    "aheadofai": {
        "name": "Ahead of AI",
        "url": "https://magazine.sebastianraschka.com/feed",
        "description": "Sebastian Raschka's ML/AI research updates and tutorials",
        "frequency": "weekly",
        "language": "en",
    },

    # === Chinese Sources ===
    "qbitai": {
        "name": "量子位",
        "url": "https://www.qbitai.com/feed",
        "description": "中国领先的AI科技媒体，报道AI前沿动态",
        "frequency": "daily",
        "language": "zh",
    },

    # === Tech Communities ===
    "hn_ai": {
        "name": "Hacker News AI",
        "url": "https://hnrss.org/newest?q=AI+OR+LLM+OR+GPT+OR+Claude&points=30",
        "description": "AI-related discussions from Hacker News (30+ points)",
        "frequency": "realtime",
        "language": "en",
    },
}

# Default source for backward compatibility
DEFAULT_SOURCE = "smol"


def fetch_rss(source_id=None, url=None):
    """Download and parse RSS from specified source

    Args:
        source_id: Source identifier (e.g., 'smol', 'importai')
        url: Direct URL to fetch (overrides source_id)

    Returns:
        Tuple of (feed, source_info) or raises exception
    """
    if url:
        rss_url = url
        source_info = {"name": "Custom", "url": url}
    elif source_id:
        if source_id not in RSS_SOURCES:
            print(json.dumps({"error": f"Unknown source: {source_id}", "available_sources": list(RSS_SOURCES.keys())}))
            sys.exit(1)
        source_info = RSS_SOURCES[source_id]
        rss_url = source_info["url"]
    else:
        source_info = RSS_SOURCES[DEFAULT_SOURCE]
        rss_url = source_info["url"]

    try:
        headers = {
            "User-Agent": "AI-Daily-Fetcher/1.0 (https://github.com/ai-daily)"
        }
        response = requests.get(rss_url, timeout=REQUEST_TIMEOUT, headers=headers)
        response.raise_for_status()
        feed = feedparser.parse(response.content)
        return feed, source_info
    except requests.RequestException as e:
        raise Exception(f"Failed to fetch RSS from {source_info['name']}: {e}")


def fetch_all_sources(source_ids=None):
    """Fetch from multiple sources in parallel

    Args:
        source_ids: List of source IDs to fetch, or None for all sources

    Returns:
        Dict mapping source_id to (feed, source_info) or error message
    """
    if source_ids is None:
        source_ids = list(RSS_SOURCES.keys())

    results = {}

    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_source = {
            executor.submit(fetch_rss, source_id): source_id
            for source_id in source_ids
        }

        for future in as_completed(future_to_source):
            source_id = future_to_source[future]
            try:
                feed, source_info = future.result()
                results[source_id] = {"feed": feed, "source_info": source_info, "success": True}
            except Exception as e:
                results[source_id] = {"error": str(e), "success": False}

    return results


def get_date_range(feed):
    """Get available date range from RSS entries

    Returns:
        tuple: (min_date, max_date) in YYYY-MM-DD format, or (None, None)
    """
    dates = []
    for entry in feed.entries:
        # Method 1: Parse from link (format: .../issues/YY-MM-DD-...)
        if hasattr(entry, 'link'):
            date_from_link = extract_date_from_link(entry.link)
            if date_from_link:
                dates.append(date_from_link)

        # Method 2: Parse from pubDate
        elif hasattr(entry, 'published_parsed') and entry.published_parsed:
            dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            dates.append(dt.strftime("%Y-%m-%d"))

    if not dates:
        return None, None

    return min(dates), max(dates)


def extract_date_from_link(link):
    """Extract date from RSS link

    Args:
        link: URL string like https://news.smol.ai/issues/26-01-13-not-much/

    Returns:
        Date string in YYYY-MM-DD format, or None
    """
    patterns = [
        r'/issues/(\d{2})-(\d{2})-(\d{2})-',  # YY-MM-DD (smol.ai)
        r'/issues/(\d{4})-(\d{2})-(\d{2})-',  # YYYY-MM-DD
        r'/p/(\d{4})-(\d{2})-(\d{2})',  # Substack format
    ]

    for pattern in patterns:
        match = re.search(pattern, link)
        if match:
            year, month, day = match.groups()
            if len(year) == 2:
                year = "20" + year
            return f"{year}-{month}-{day}"

    return None


def extract_date_from_entry(entry):
    """Extract date from an RSS entry using multiple methods

    Args:
        entry: feedparser entry object

    Returns:
        Date string in YYYY-MM-DD format, or None
    """
    # Method 1: Parse from link
    if hasattr(entry, 'link') and entry.link:
        date_from_link = extract_date_from_link(entry.link)
        if date_from_link:
            return date_from_link

    # Method 2: Parse from pubDate
    if hasattr(entry, 'published_parsed') and entry.published_parsed:
        dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        return dt.strftime("%Y-%m-%d")

    # Method 3: Parse from updated
    if hasattr(entry, 'updated_parsed') and entry.updated_parsed:
        dt = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
        return dt.strftime("%Y-%m-%d")

    return None


def get_latest_entries(feed, limit=10):
    """Get the latest entries from a feed

    Args:
        feed: Feedparser parsed feed
        limit: Maximum number of entries to return

    Returns:
        List of entry dicts with extracted content
    """
    entries = []
    for entry in feed.entries[:limit]:
        content = extract_entry_content(entry)
        content["date"] = extract_date_from_entry(entry)
        entries.append(content)
    return entries


def list_sources():
    """Return information about available RSS sources"""
    sources = []
    for source_id, info in RSS_SOURCES.items():
        sources.append({
            "id": source_id,
            "name": info["name"],
            "description": info["description"],
            "frequency": info["frequency"],
            "language": info["language"],
        })
    return sources


def get_content_by_date(feed, target_date):
    """Extract content for a specific date

    Args:
        feed: Feedparser parsed feed
        target_date: Date string in YYYY-MM-DD format

    Returns:
        dict with keys: title, link, content, pubDate, or None if not found
    """
    for entry in feed.entries:
        # Check by link date
        if hasattr(entry, 'link'):
            date_from_link = extract_date_from_link(entry.link)
            if date_from_link and date_from_link == target_date:
                return extract_entry_content(entry)

        # Check by pubDate
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            entry_date = dt.strftime("%Y-%m-%d")
            if entry_date == target_date:
                return extract_entry_content(entry)

    return None


def extract_entry_content(entry):
    """Extract content from an RSS entry

    Returns:
        dict with keys: title, link, content, pubDate, truncated (optional)
    """
    content = {
        "title": entry.get("title", ""),
        "link": entry.get("link", ""),
        "pubDate": ""
    }

    # Get published date
    if hasattr(entry, 'published'):
        content["pubDate"] = entry.published

    # Get full content
    if hasattr(entry, 'content') and entry.content:
        raw_content = entry.content[0].get('value', '')
    elif hasattr(entry, 'summary'):
        raw_content = entry.summary
    else:
        raw_content = content.get("title", "")

    # Clean HTML entities
    raw_content = raw_content.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')

    # Truncate content if too long (to avoid exceeding 256KB limit)
    if len(raw_content) > MAX_CONTENT_LENGTH:
        content["content"] = raw_content[:MAX_CONTENT_LENGTH] + "...[内容已截断]"
        content["truncated"] = True
    else:
        content["content"] = raw_content

    return content


def save_output(data, output_path=None, auto=False, format="md"):
    """Save output to file

    Args:
        data: Dict to save
        output_path: File path to save to, or None for auto-generated path
        auto: If True, auto-generate filename based on date
        format: Output format - "md" (default) or "json"

    Returns:
        Path to saved file, or None if not saving
    """
    if not output_path and not auto:
        return None

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Determine file extension
    ext = "md" if format == "md" else "json"

    if output_path == "auto" or auto:
        # Auto-generate filename: news_YYYY-MM-DD.md
        date_str = datetime.now().strftime("%Y-%m-%d")
        output_path = OUTPUT_DIR / f"news_{date_str}.{ext}"
    else:
        output_path = Path(output_path)
        # If relative path, put in OUTPUT_DIR
        if not output_path.is_absolute():
            output_path = OUTPUT_DIR / output_path

    with open(output_path, 'w', encoding='utf-8') as f:
        if format == "md":
            md_content = convert_to_markdown(data)
            f.write(md_content)
        else:
            json.dump(data, f, indent=2, ensure_ascii=False)

    return output_path


def convert_to_markdown(data):
    """Convert news data to Markdown format

    Args:
        data: Dict containing news data

    Returns:
        Markdown string
    """
    lines = []
    date_str = datetime.now().strftime("%Y年%m月%d日")
    lines.append(f"# AI Daily · {date_str}\n")

    # Handle multi-source format
    if "sources" in data:
        for source_id, source_data in data["sources"].items():
            if "error" in source_data:
                continue

            source_name = source_data.get("name", source_id)
            lines.append(f"\n## {source_name}\n")

            entries = source_data.get("entries", [])
            if not entries and "content" in source_data:
                entries = [source_data["content"]]

            for entry in entries:
                title = entry.get("title", "无标题")
                link = entry.get("link", "")
                content = entry.get("content", "")
                pub_date = entry.get("pubDate", "")

                lines.append(f"### {title}\n")
                if pub_date:
                    lines.append(f"*{pub_date}*\n")
                if content:
                    # Clean HTML tags for markdown
                    clean_content = re.sub(r'<[^>]+>', '', content)
                    # Truncate for readability
                    if len(clean_content) > 500:
                        clean_content = clean_content[:500] + "..."
                    lines.append(f"{clean_content}\n")
                if link:
                    lines.append(f"\n📎 原文链接: [{source_name}]({link})\n")
                lines.append("")

    # Handle single source format
    elif "entries" in data:
        source_name = data.get("source", "Unknown")
        lines.append(f"\n## {source_name}\n")

        for entry in data["entries"]:
            title = entry.get("title", "无标题")
            link = entry.get("link", "")
            content = entry.get("content", "")

            lines.append(f"### {title}\n")
            if content:
                clean_content = re.sub(r'<[^>]+>', '', content)
                if len(clean_content) > 500:
                    clean_content = clean_content[:500] + "..."
                lines.append(f"{clean_content}\n")
            if link:
                lines.append(f"\n📎 原文链接: [{source_name}]({link})\n")
            lines.append("")

    lines.append("\n---")
    lines.append(f"*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

    return "\n".join(lines)


def entry_age_hours(entry):
    """Return how many hours ago this entry was published (None if unknown)."""
    if hasattr(entry, 'published_parsed') and entry.published_parsed:
        pub = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - pub).total_seconds() / 3600
    return None


def resolve_date(date_expr):
    """Resolve a date expression to YYYY-MM-DD.

    Accepts:
      'today'     → current date
      'yesterday' → today - 1 day  (default)
      'day-before'→ today - 2 days
      'YYYY-MM-DD'→ literal date
    """
    now = datetime.now(timezone.utc)
    if date_expr in (None, "", "yesterday"):
        return (now - timedelta(days=1)).strftime("%Y-%m-%d")
    elif date_expr == "today":
        return now.strftime("%Y-%m-%d")
    elif date_expr == "day-before":
        return (now - timedelta(days=2)).strftime("%Y-%m-%d")
    else:
        # Assume YYYY-MM-DD literal
        return date_expr


def load_env_config():
    """Load news_daily_date (and other news_daily_* fields) from ~/.claude/env.json."""
    env_path = Path.home() / ".claude" / "env.json"
    if env_path.exists():
        try:
            return json.loads(env_path.read_text())
        except Exception:
            pass
    return {}


def smart_fetch(limit=5, date_expr=None):
    """Smart mode: smol.ai latest digest + realtime HN supplement when stale.

    Args:
        limit: max entries per source
        date_expr: 'today' | 'yesterday' | 'day-before' | 'YYYY-MM-DD' | None
                   None → read from env.json news_daily_date (default: 'yesterday')
    """
    # Resolve target date
    if date_expr is None:
        cfg = load_env_config()
        date_expr = cfg.get("news_daily_date", "yesterday")
    target_date = resolve_date(date_expr)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    output = {
        "mode": "smart",
        "requested_date": target_date,
        "sources": {},
    }

    # ── 1. Fetch smol.ai ──
    try:
        feed, source_info = fetch_rss("smol")
        entries = get_latest_entries(feed, limit)
        newest_age = None
        if feed.entries and hasattr(feed.entries[0], 'published_parsed') and feed.entries[0].published_parsed:
            newest_age = entry_age_hours(feed.entries[0])

        actual_date = entries[0]["date"] if entries else None
        # Stale if smol's latest is older than target_date
        stale = (actual_date is None) or (actual_date < target_date)

        output["sources"]["smol"] = {
            "name": source_info["name"],
            "entries": entries,
            "count": len(entries),
            "actual_date": actual_date,
            "age_hours": round(newest_age, 1) if newest_age is not None else None,
            "stale": stale,
        }
        if stale and actual_date:
            output["note"] = (
                f"smol.ai 最新内容来自 {actual_date}（目标日期 {target_date}），"
                f"已自动补充 Hacker News 实时内容"
            )
    except Exception as e:
        output["sources"]["smol"] = {"error": str(e)}
        stale = True

    # ── 2. Supplement with HN when stale ──
    if stale:
        try:
            feed_hn, source_hn = fetch_rss("hn_ai")
            # Filter to entries published today or yesterday
            hn_entries = []
            for entry in feed_hn.entries[:30]:
                age = entry_age_hours(entry)
                if age is not None and age <= 48:
                    item = extract_entry_content(entry)
                    item["date"] = extract_date_from_entry(entry)
                    item["age_hours"] = round(age, 1)
                    hn_entries.append(item)
                if len(hn_entries) >= limit:
                    break

            output["sources"]["hn_ai"] = {
                "name": source_hn["name"],
                "entries": hn_entries,
                "count": len(hn_entries),
                "note": "实时内容（最近 48 小时）",
            }
        except Exception as e:
            output["sources"]["hn_ai"] = {"error": str(e)}

    return output


def main():
    parser = argparse.ArgumentParser(description='Fetch AI news from multiple sources')
    parser.add_argument('--smart', action='store_true',
                       help='Smart mode: smol.ai latest + realtime HN when stale (recommended default)')
    parser.add_argument('--date-range', action='store_true', help='Show available date range')
    parser.add_argument('--date', type=str, help='Get content for specific date (YYYY-MM-DD)')
    parser.add_argument('--latest', action='store_true', help='Get the latest available content')
    parser.add_argument('--relative', type=str, choices=['yesterday', 'today', 'day-before'],
                       help='Relative date: yesterday, today, day-before')

    # Multi-source arguments
    parser.add_argument('--source', '-s', type=str, default=DEFAULT_SOURCE,
                       help=f'Source to fetch from (default: {DEFAULT_SOURCE}). Use --list-sources to see all.')
    parser.add_argument('--sources', type=str, nargs='+',
                       help='Multiple sources to fetch from (e.g., --sources smol importai)')
    parser.add_argument('--all-sources', action='store_true',
                       help='Fetch from all available sources')
    parser.add_argument('--list-sources', action='store_true',
                       help='List all available RSS sources')
    parser.add_argument('--limit', type=int, default=10,
                       help='Maximum number of entries to return per source (default: 10)')
    parser.add_argument('--output', '-o', type=str,
                       help='Save output to file (e.g., --output news.json). Auto-generates filename if "auto" is specified.')

    args = parser.parse_args()

    # Smart mode (recommended default)
    if args.smart:
        output = smart_fetch(limit=args.limit, date_expr=args.date)
        print(json.dumps(output, indent=2, ensure_ascii=False))
        return

    # List sources mode
    if args.list_sources:
        sources = list_sources()
        print(json.dumps({"sources": sources}, indent=2, ensure_ascii=False))
        return

    # Determine which sources to fetch
    if args.all_sources:
        source_ids = list(RSS_SOURCES.keys())
        # Auto-reduce limit for all-sources to avoid exceeding 256KB
        if args.limit == 10:  # Only override if using default
            args.limit = DEFAULT_LIMIT_ALL_SOURCES
    elif args.sources:
        source_ids = args.sources
        # Auto-reduce limit for multiple sources
        if len(args.sources) > 3 and args.limit == 10:
            args.limit = DEFAULT_LIMIT_ALL_SOURCES
    else:
        source_ids = [args.source]

    # Multi-source fetch mode
    if len(source_ids) > 1:
        results = fetch_all_sources(source_ids)
        output = {"sources": {}}

        for source_id, result in results.items():
            if result["success"]:
                feed = result["feed"]
                source_info = result["source_info"]

                if args.latest:
                    entries = get_latest_entries(feed, args.limit)
                    output["sources"][source_id] = {
                        "name": source_info["name"],
                        "entries": entries,
                        "count": len(entries),
                    }
                elif args.date_range:
                    min_date, max_date = get_date_range(feed)
                    output["sources"][source_id] = {
                        "name": source_info["name"],
                        "min_date": min_date,
                        "max_date": max_date,
                        "total_entries": len(feed.entries),
                    }
                else:
                    # Get by date
                    target_date = calculate_target_date(args)
                    content = get_content_by_date(feed, target_date)
                    if content:
                        output["sources"][source_id] = {
                            "name": source_info["name"],
                            "content": content,
                        }
                    else:
                        # Try to get latest entries instead
                        entries = get_latest_entries(feed, args.limit)
                        output["sources"][source_id] = {
                            "name": source_info["name"],
                            "entries": entries,
                            "note": f"No exact match for {target_date}, showing latest entries",
                        }
            else:
                output["sources"][source_id] = {
                    "error": result["error"],
                }

        # Save output if requested
        if args.output:
            saved_path = save_output(output, args.output)
            output["_saved_to"] = str(saved_path)

        print(json.dumps(output, indent=2, ensure_ascii=False))
        return

    # Single source fetch (original behavior)
    try:
        feed, source_info = fetch_rss(source_ids[0])
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

    # Date range mode
    if args.date_range:
        min_date, max_date = get_date_range(feed)
        print(json.dumps({
            "source": source_info["name"],
            "min_date": min_date,
            "max_date": max_date,
            "total_entries": len(feed.entries)
        }, indent=2))
        return

    # Latest mode - get most recent available content
    if args.latest:
        entries = get_latest_entries(feed, args.limit)
        if entries:
            print(json.dumps({
                "source": source_info["name"],
                "entries": entries,
                "count": len(entries),
            }, indent=2, ensure_ascii=False))
            return
        print(json.dumps({"error": "no_content", "message": "No content available in RSS"}, indent=2))
        return

    # Calculate target date
    target_date = calculate_target_date(args)

    # Get content
    content = get_content_by_date(feed, target_date)

    if content:
        content["source"] = source_info["name"]
        print(json.dumps(content, indent=2, ensure_ascii=False))
    else:
        # Return empty result with available range
        min_date, max_date = get_date_range(feed)
        print(json.dumps({
            "error": "not_found",
            "message": f"No content found for {target_date}",
            "source": source_info["name"],
            "target_date": target_date,
            "available_range": {
                "min": min_date,
                "max": max_date
            }
        }, indent=2))


def calculate_target_date(args):
    """Calculate target date from arguments"""
    if args.relative:
        if args.relative == 'yesterday':
            return (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
        elif args.relative == 'day-before':
            return (datetime.now(timezone.utc) - timedelta(days=2)).strftime("%Y-%m-%d")
        else:  # today
            return datetime.now(timezone.utc).strftime("%Y-%m-%d")
    elif args.date:
        return args.date
    else:
        # Default: yesterday
        return (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")


if __name__ == "__main__":
    main()

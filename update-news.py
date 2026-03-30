import json
import re
from datetime import datetime, timezone
 
import feedparser

FEEDS = [
    "https://www.edsurge.com/news.rss",
    "https://techcrunch.com/tag/edtech/feed/",
    "https://www.holoniq.com/feed",
 "https://www.google.com/alerts/feeds/04612595539817232726/1950645162679430176"
]

KEYWORDS = [
    "edtech", "education technology",
    "education startup", "startup",
    "raised", "funding", "investment", "series",
    "acquired", "acquisition", "merger",
    "launch", "launches", "announces", "product",
    "platform", "software", "ai tutor",
    "learning platform", "school software"
]

CATEGORY_RULES = {
    "Funding": ["funding", "raised", "seed", "series a", "series b", "series c", "investment"],
    "Acquisition": ["acquisition", "acquire", "acquired", "merger"],
    "Product": ["launch", "launches", "product", "platform", "announces", "announcement"],
    "Startup": ["startup", "founder", "early-stage"]
}


def clean_text(value: str) -> str:
    if not value:
        return ""
    value = re.sub(r"<[^>]+>", "", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def is_relevant(text: str) -> bool:
    text = text.lower()
    return any(keyword in text for keyword in KEYWORDS)


def choose_category(text: str) -> str:
    text = text.lower()
    for category, words in CATEGORY_RULES.items():
        if any(word in text for word in words):
            return category
    return "General"


def short_summary(text: str, max_len: int = 220) -> str:
    text = clean_text(text)
    if len(text) <= max_len:
        return text
    return text[:max_len].rsplit(" ", 1)[0] + "..."


def parse_feed():
    articles = []
    seen_links = set()

    for url in FEEDS:
        feed = feedparser.parse(url)
        source = clean_text(feed.feed.get("title", "Unknown source"))

        for entry in feed.entries:
            title = clean_text(entry.get("title", ""))
            summary = clean_text(entry.get("summary", ""))
            link = entry.get("link", "").strip()
            published = clean_text(entry.get("published", ""))

            combined = f"{title} {summary}"

            if not link or link in seen_links:
                continue
            if not is_relevant(combined):
                continue

# must include at least one company/action signal
if not any(word in combined.lower() for word in [
    "raised", "funding", "acquired", "acquisition",
    "launch", "announces", "startup", "platform"
]):
    continue

            seen_links.add(link)
            articles.append({
                "title": title,
                "summary": short_summary(summary or title),
                "link": link,
                "source": source,
                "published": published,
                "category": choose_category(combined)
            })

    return articles[:25]


def main():
    articles = parse_feed()
    output = {
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "articles": articles
    }

    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(articles)} articles to news.json")


if __name__ == "__main__":
    main()

"""
https://openlibrary.org/dev/docs/api/books

This script makes several calls to the Open Library API to:
1. Look up books by ISBN using the Books API
2. Search for books by topic using the Search API
3. Compare page counts and publication years
4. Find the most prolific author from the results
5. Display a reading-time estimate for each book
"""

import requests

BOOKS_URL = "https://openlibrary.org/api/books"
SEARCH_URL = "https://openlibrary.org/search.json"

# A selection of well-known ISBNs to look up
ISBNS = {
    "978-0-13-468599-1": "The Pragmatic Programmer",
    "978-0-596-00712-6": "Head First Design Patterns",
    "978-0-201-63361-0": "Design Patterns (GoF)",
    "978-0-13-235088-4": "Clean Code",
    "978-0-596-51774-8": "JavaScript: The Good Parts",
    "978-0-59-651798-4": "Learning Python",
}

SEARCH_TOPICS = ["artificial intelligence", "machine learning"]

# Average reading speed: ~250 words/page, ~2 min/page
MINUTES_PER_PAGE = 2


def lookup_by_isbn(isbn: str) -> dict | None:
    """Look up a single book by ISBN using the Books API (bibkeys endpoint)."""
    clean = isbn.replace("-", "")
    params = {
        "bibkeys": f"ISBN:{clean}",
        "format": "json",
        "jscmd": "data",
    }
    response = requests.get(BOOKS_URL, params=params)
    response.raise_for_status()
    data = response.json()
    key = f"ISBN:{clean}"
    if key not in data:
        return None
    book = data[key]
    return {
        "title": book.get("title", "Unknown"),
        "authors": [a["name"] for a in book.get("authors", [])],
        "publishers": [p["name"] for p in book.get("publishers", [])],
        "publish_date": book.get("publish_date", "Unknown"),
        "pages": book.get("number_of_pages", 0),
        "cover_url": book.get("cover", {}).get("medium", "N/A"),
        "isbn": isbn,
    }


def search_books(query: str, limit: int = 5) -> list[dict]:
    """Search for books by query string using the Search API."""
    params = {
        "q": query,
        "limit": limit,
        "fields": "title,author_name,first_publish_year,number_of_pages_median,subject",
    }
    response = requests.get(SEARCH_URL, params=params)
    response.raise_for_status()
    data = response.json()
    results = []
    for doc in data.get("docs", []):
        results.append({
            "title": doc.get("title", "Unknown"),
            "authors": doc.get("author_name", ["Unknown"]),
            "year": doc.get("first_publish_year", None),
            "pages": doc.get("number_of_pages_median", None),
            "subjects": doc.get("subject", [])[:5],
        })
    return results


def estimate_reading_time(pages: int) -> str:
    """Estimate reading time from page count."""
    if not pages:
        return "Unknown"
    total_min = pages * MINUTES_PER_PAGE
    hours, minutes = divmod(total_min, 60)
    if hours > 0:
        return f"{hours}h {minutes}min"
    return f"{minutes}min"


# ---------------------------------------------------------------------------
# 1. Look up books by ISBN
# ---------------------------------------------------------------------------
print("=" * 65)
print("  BOOK LOOKUP BY ISBN (Open Library Books API)")
print("=" * 65)

isbn_results = []
for isbn, expected_title in ISBNS.items():
    book = lookup_by_isbn(isbn)
    if book:
        isbn_results.append(book)
        reading = estimate_reading_time(book["pages"])
        print(f"\n📖 {book['title']}")
        print(f"   Authors:      {', '.join(book['authors']) or 'N/A'}")
        print(f"   Publisher:    {', '.join(book['publishers']) or 'N/A'}")
        print(f"   Published:    {book['publish_date']}")
        print(f"   Pages:        {book['pages'] or 'N/A'}")
        print(f"   Reading time: {reading}")
    else:
        print(f"\n❌ ISBN {isbn} ({expected_title}) — not found")

# ---------------------------------------------------------------------------
# 2. Compare page counts
# ---------------------------------------------------------------------------
print("\n" + "=" * 65)
print("  PAGE COUNT RANKING")
print("=" * 65)

books_with_pages = [b for b in isbn_results if b["pages"]]
if books_with_pages:
    ranking = sorted(books_with_pages, key=lambda b: b["pages"], reverse=True)
    for i, book in enumerate(ranking, 1):
        bar = "█" * (book["pages"] // 20)
        print(f"  {i}. {book['title'][:40]:<40s} {book['pages']:>4} pp  {bar}")

    longest = ranking[0]
    shortest = ranking[-1]
    avg_pages = sum(b["pages"] for b in ranking) / len(ranking)
    print(f"\n  📈 Longest:  {longest['title']} ({longest['pages']} pp)")
    print(f"  📉 Shortest: {shortest['title']} ({shortest['pages']} pp)")
    print(f"  📏 Average:  {avg_pages:.0f} pages")
else:
    print("  No page data available for comparison.")

# ---------------------------------------------------------------------------
# 3. Search for books by topic
# ---------------------------------------------------------------------------
print("\n" + "=" * 65)
print("  BOOK SEARCH BY TOPIC")
print("=" * 65)

all_search_results = []
for topic in SEARCH_TOPICS:
    print(f"\n🔍 Topic: \"{topic}\"")
    print(f"  {'-' * 55}")
    results = search_books(topic, limit=5)
    all_search_results.extend(results)
    for j, book in enumerate(results, 1):
        authors = ", ".join(book["authors"][:2])
        year = book["year"] or "?"
        pages = book["pages"] or "?"
        print(f"  {j}. {book['title'][:45]:<45s} ({year}) {pages} pp")
        print(f"     by {authors}")

# ---------------------------------------------------------------------------
# 4. Most prolific authors from search results
# ---------------------------------------------------------------------------
print("\n" + "=" * 65)
print("  MOST FREQUENT AUTHORS IN SEARCH RESULTS")
print("=" * 65)

author_count: dict[str, int] = {}
for book in all_search_results:
    for author in book["authors"]:
        author_count[author] = author_count.get(author, 0) + 1

top_authors = sorted(author_count.items(), key=lambda x: x[1], reverse=True)[:8]
for author, count in top_authors:
    bar = "★ " * count
    print(f"  {author:<35s} {count} book(s)  {bar}")

# ---------------------------------------------------------------------------
# 5. Publication timeline from search results
# ---------------------------------------------------------------------------
print("\n" + "=" * 65)
print("  PUBLICATION TIMELINE")
print("=" * 65)

books_with_year = [b for b in all_search_results if b["year"]]
if books_with_year:
    by_year = sorted(books_with_year, key=lambda b: b["year"])
    oldest = by_year[0]
    newest = by_year[-1]
    span = newest["year"] - oldest["year"]
    print(f"\n  Oldest: {oldest['title'][:45]} ({oldest['year']})")
    print(f"  Newest: {newest['title'][:45]} ({newest['year']})")
    print(f"  Span:   {span} years")

    # Decade distribution
    decades: dict[str, int] = {}
    for book in books_with_year:
        decade = f"{(book['year'] // 10) * 10}s"
        decades[decade] = decades.get(decade, 0) + 1

    print(f"\n  Books by decade:")
    for decade in sorted(decades):
        bar = "█" * decades[decade]
        print(f"    {decade}: {decades[decade]:2d}  {bar}")
else:
    print("  No publication year data available.")

print("\n✅ All API calls completed successfully.")

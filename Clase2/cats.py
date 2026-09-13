"""
https://catfact.ninja/fact

This script makes several calls to the Cat Fact API to:
1. Fetch a single random cat fact
2. Fetch multiple facts and find the longest and shortest ones
3. Classify facts by length (short / medium / long)
4. Display a summary with statistics
"""

import requests

BASE_URL = "https://catfact.ninja/fact"
NUM_FACTS = 10


def get_random_fact() -> dict:
    """Fetch a single random cat fact from the API."""
    response = requests.get(BASE_URL)
    response.raise_for_status()
    data = response.json()
    return {
        "fact": data["fact"],
        "length": data["length"],
    }


def classify_by_length(length: int) -> str:
    """Classify a fact as short, medium or long based on character count."""
    if length < 80:
        return "Short"
    elif length < 150:
        return "Medium"
    else:
        return "Long"


# ---------------------------------------------------------------------------
# 1. Fetch a single random cat fact
# ---------------------------------------------------------------------------
print("=" * 60)
print("  RANDOM CAT FACT")
print("=" * 60)

single = get_random_fact()
print(f"\n🐱 {single['fact']}")
print(f"   (Length: {single['length']} characters)")

# ---------------------------------------------------------------------------
# 2. Fetch multiple facts
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print(f"  FETCHING {NUM_FACTS} RANDOM CAT FACTS")
print("=" * 60)

facts = []
for i in range(NUM_FACTS):
    fact = get_random_fact()
    facts.append(fact)
    category = classify_by_length(fact["length"])
    print(f"\n  {i + 1}. [{category:6s}] ({fact['length']:3d} chars) {fact['fact']}")

# ---------------------------------------------------------------------------
# 3. Statistics
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print("  STATISTICS")
print("=" * 60)

longest = max(facts, key=lambda f: f["length"])
shortest = min(facts, key=lambda f: f["length"])
avg_length = sum(f["length"] for f in facts) / len(facts)

print(f"\n  📏 Average length:  {avg_length:.1f} characters")
print(f"  📈 Longest fact:    {longest['length']} chars")
print(f"     \"{longest['fact']}\"")
print(f"  📉 Shortest fact:   {shortest['length']} chars")
print(f"     \"{shortest['fact']}\"")

# ---------------------------------------------------------------------------
# 4. Classification summary
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print("  CLASSIFICATION SUMMARY")
print("=" * 60)

categories = {"Short": [], "Medium": [], "Long": []}
for fact in facts:
    cat = classify_by_length(fact["length"])
    categories[cat].append(fact)

for cat_name, cat_facts in categories.items():
    count = len(cat_facts)
    pct = (count / len(facts)) * 100
    bar = "█" * count + "░" * (NUM_FACTS - count)
    print(f"  {cat_name:6s}: {count:2d} ({pct:4.0f}%)  {bar}")

# ---------------------------------------------------------------------------
# 5. Unique word analysis across all facts
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print("  WORD ANALYSIS")
print("=" * 60)

all_words = []
for fact in facts:
    words = fact["fact"].lower().replace(",", "").replace(".", "").split()
    all_words.extend(words)

unique_words = set(all_words)
word_freq = {w: all_words.count(w) for w in unique_words}
top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]

print(f"\n  Total words:  {len(all_words)}")
print(f"  Unique words: {len(unique_words)}")
print(f"\n  Top 10 most frequent words:")
for word, count in top_words:
    print(f"    {word:15s} × {count}")

print("\n✅ All API calls completed successfully.")

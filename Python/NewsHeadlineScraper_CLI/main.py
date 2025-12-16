from scraper import fetch_headlines
from config import DEFAULT_URL, MAX_HEADLINES, DELAY  # Added DELAY import here

def display_headlines(headlines):
    if not headlines:
        print("No headlines found. Try again later.")
        return

    print("\n🔥 Top Headlines:")
    print("=" * 50)
    for i, headline in enumerate(headlines[:MAX_HEADLINES], 1):  # Fixed the start index
        print(f"{i}. {headline}")
    print("=" * 50)
    print(f"ℹ️  Showing {min(len(headlines), MAX_HEADLINES)} of {len(headlines)} headlines")

def main():
    print("=" * 50)
    print("📰 Safe Hacker News Scraper")
    print("=" * 50)
    print(f"⏳ Fetching headlines (with {DELAY} second delay for safety)...")

    headlines = fetch_headlines(DEFAULT_URL)
    display_headlines(headlines)

if __name__ == "__main__":
    main()
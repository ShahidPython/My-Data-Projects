# Website to scrape (Hacker News)
DEFAULT_URL = "https://news.ycombinator.com/"
MAX_HEADLINES = 10  # Limit to 10 headlines

# Safety settings
TIMEOUT = 10        # Don't wait more than 10 seconds
DELAY = 3           # Wait 3 seconds between requests
CACHE_EXPIRY = 3600 # Cache results for 1 hour (3600 seconds)

# first prompt
Implement search_listings in tools.py. Use load_listings() from utils/data_loader.py. it must do the following: 1. Load all listings with load_listings().
        2. Filter by max_price and size (if provided).
        3. Score each remaining listing by keyword overlap with `description`.
        4. Drop any listings with a score of 0 (no relevant matches).
        5. Sort by score, highest first, and return the listing dicts. Here are the specs for it: ### Tool 1: search_listings

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
Searches the listings dataset and returns up to 8 matching items, filtered by description, size, and max_price.

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `description` (str): A natural language description of the item, matched against listing fields (title, description, style_tags, etc.). Already stripped of size/price by parse_query.
- `size` (str): The user's clothing size. May be none to skip size filter.
- `max_price` (float): Maximum price user is looking for. May be none to skip price filter.

**What it returns:**
<!-- Describe the return value — what fields does a result contain? -->
- `results` (list): Results is an array of size 8 which contains listings. Each listing is a dictionary describing an item (listing) with its id, title, description, size, condition, etc. These are pulled from the listings.json dataset if they are matching the user provided parameters. 

**What happens if it fails or returns nothing:**
<!-- What should the agent do if no listings match? -->
Tell user we were not able to find good listing matches. Ask user to try a new prompt if they would like to continue.

---

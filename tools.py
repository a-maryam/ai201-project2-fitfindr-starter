"""
tools.py

The three required FitFindr tools. Each tool is a standalone function that
can be called and tested independently before being wired into the agent loop.

Complete and test each tool before moving to agent.py.

Tools:
    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)              → str
    create_fit_card(outfit, new_item)               → str
"""

import json
import os
import re

from dotenv import load_dotenv
from groq import Groq

from utils.data_loader import load_listings

load_dotenv()


# ── Groq client ───────────────────────────────────────────────────────────────

def _get_groq_client():
    """Initialize and return a Groq client using GROQ_API_KEY from .env."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not set. Add it to a .env file in the project root."
        )
    return Groq(api_key=api_key)


# ── Tool 4: parse_query ───────────────────────────────────────────────────────

def parse_query(query: str) -> dict:
    """
    Parse a natural language query into structured search parameters.

    Args:
        query: Natural language query, e.g. "vintage graphic tee under $30, size M"

    Returns:
        A dict with keys:
            description (str):        Query text with size/price references removed.
            size        (str | None):  Clothing size if present, else None.
            max_price   (float | None): Price ceiling if present, else None.

        Never raises — on any parsing error, description defaults to the full
        query string and size/max_price default to None.
    """
    client = _get_groq_client()

    prompt = (
        "Extract structured fields from this clothing search query.\n"
        "Return ONLY a JSON object with exactly these three keys:\n"
        '  "description": the item description with size and price references removed,\n'
        '  "size": clothing size string if present (e.g. "XS", "S", "M", "L", "XL", "8"), or null,\n'
        '  "max_price": maximum price as a float if present, or null.\n\n'
        f'Query: "{query}"\n\n'
        "JSON object:"
    )

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
        )
        content = response.choices[0].message.content.strip()

        # Strip markdown code fences if present
        match = re.search(r"\{.*\}", content, re.DOTALL)
        raw = match.group(0) if match else content
        parsed = json.loads(raw)

        return {
            "description": parsed.get("description") or query,
            "size": parsed.get("size") or None,
            "max_price": float(parsed["max_price"]) if parsed.get("max_price") is not None else None,
        }
    except Exception:
        return {"description": query, "size": None, "max_price": None}


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the mock listings dataset for items matching the description,
    optional size, and optional price ceiling.

    Args:
        description: Keywords describing what the user is looking for
                     (e.g., "vintage graphic tee").
        size:        Size string to filter by, or None to skip size filtering.
                     Matching is case-insensitive (e.g., "M" matches "S/M").
        max_price:   Maximum price (inclusive), or None to skip price filtering.

    Returns:
        A list of matching listing dicts, sorted by relevance (best match first).
        Returns an empty list if nothing matches — does NOT raise an exception.

    Each listing dict has the following fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand, platform

    TODO:
        1. Load all listings with load_listings().
        2. Filter by max_price and size (if provided).
        3. Score each remaining listing by keyword overlap with `description`.
        4. Drop any listings with a score of 0 (no relevant matches).
        5. Sort by score, highest first, and return the listing dicts.

    Before writing code, fill in the Tool 1 section of planning.md.
    """
    listings = load_listings()

    filtered = []
    for listing in listings:
        if max_price is not None and listing["price"] > max_price:
            continue
        if size is not None and size.upper() not in listing["size"].upper():
            continue
        filtered.append(listing)

    keywords = set(description.lower().split())

    def score(listing):
        searchable = " ".join([
            listing.get("title", ""),
            listing.get("description", ""),
            listing.get("category", ""),
            listing.get("brand", "") or "",
            " ".join(listing.get("style_tags", [])),
            " ".join(listing.get("colors", [])),
        ]).lower()
        return sum(1 for kw in keywords if kw in searchable)

    scored = [(score(l), l) for l in filtered]
    scored = [(s, l) for s, l in scored if s > 0]
    scored.sort(key=lambda x: x[0], reverse=True)

    return [l for _, l in scored[:8]]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest 1–2 complete outfits.

    Args:
        new_item: A listing dict (the item the user is considering buying).
        wardrobe: A wardrobe dict with an 'items' key containing a list of
                  wardrobe item dicts. May be empty — handle this gracefully.

    Returns:
        A non-empty string with outfit suggestions.
        If the wardrobe is empty, offer general styling advice for the item
        rather than raising an exception or returning an empty string.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If empty: call the LLM with a prompt for general styling ideas
           (what kinds of items pair well, what vibe it suits, etc.).
        3. If not empty: format the wardrobe items into a prompt and ask
           the LLM to suggest specific outfit combinations using the new item
           and named pieces from the wardrobe.
        4. Return the LLM's response as a string.

    Before writing code, fill in the Tool 2 section of planning.md.
    """
    client = _get_groq_client()

    item_desc = (
        f"Title: {new_item.get('title', 'Unknown item')}\n"
        f"Category: {new_item.get('category', '')}\n"
        f"Colors: {', '.join(new_item.get('colors', []))}\n"
        f"Style tags: {', '.join(new_item.get('style_tags', []))}\n"
        f"Description: {new_item.get('description', '')}"
    )

    items = wardrobe.get("items", [])

    if not items:
        prompt = (
            "You are a personal stylist with expertise in thrift and secondhand fashion.\n\n"
            f"A user is considering buying this item:\n{item_desc}\n\n"
            "Their wardrobe is empty. Give general styling advice for this item: "
            "what kinds of pieces pair well with it, what vibe or aesthetic it suits, "
            "and how to build an outfit around it from scratch. Keep it concise and specific."
        )
    else:
        wardrobe_lines = []
        for item in items:
            line = f"- {item.get('name', 'Unknown')} ({item.get('category', '')})"
            colors = item.get("colors", [])
            tags = item.get("style_tags", [])
            if colors:
                line += f", colors: {', '.join(colors)}"
            if tags:
                line += f", style: {', '.join(tags)}"
            notes = item.get("notes")
            if notes:
                line += f" [{notes}]"
            wardrobe_lines.append(line)

        wardrobe_desc = "\n".join(wardrobe_lines)

        prompt = (
            "You are a personal stylist with expertise in thrift and secondhand fashion.\n\n"
            f"A user is considering buying this item:\n{item_desc}\n\n"
            f"Their current wardrobe includes:\n{wardrobe_desc}\n\n"
            "Suggest 1–2 complete outfits that incorporate the new item alongside specific "
            "pieces from their wardrobe. Name the wardrobe items by name. Describe the vibe "
            "of each outfit. Keep suggestions concise and practical."
        )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )

    return response.choices[0].message.content


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Generate a short, shareable outfit caption for the thrifted find.

    Args:
        outfit:   The outfit suggestion string from suggest_outfit().
        new_item: The listing dict for the thrifted item.

    Returns:
        A 2–4 sentence string usable as an Instagram/TikTok caption.
        If outfit is empty or missing, return a descriptive error message
        string — do NOT raise an exception.

    The caption should:
    - Feel casual and authentic (like a real OOTD post, not a product description)
    - Mention the item name, price, and platform naturally (once each)
    - Capture the outfit vibe in specific terms
    - Sound different each time for different inputs (use higher LLM temperature)

    TODO:
        1. Guard against an empty or whitespace-only outfit string.
        2. Build a prompt that gives the LLM the item details and the outfit,
           and asks for a caption matching the style guidelines above.
        3. Call the LLM and return the response.

    Before writing code, fill in the Tool 3 section of planning.md.
    """
    if not outfit or not outfit.strip():
        client = _get_groq_client()
        title = new_item.get("title", "Unknown item")
        price = new_item.get("price", "?")
        platform = new_item.get("platform", "a thrift app")
        colors = ", ".join(new_item.get("colors", []))
        style_tags = ", ".join(new_item.get("style_tags", []))
        description = new_item.get("description", "")

        fallback_prompt = (
            "You are a personal stylist. A user is considering buying this thrifted item "
            "but we don't have a full outfit suggestion yet. Give them 1–2 quick outfit ideas "
            "for how they could wear it — what to pair it with, what vibe it suits.\n\n"
            f"Item: {title}\nColors: {colors}\nStyle: {style_tags}\nDescription: {description}\n\n"
            "Keep it concise and specific. Return only the outfit suggestions."
        )
        outfit_suggestions = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": fallback_prompt}],
            temperature=0.7,
        ).choices[0].message.content

        return (
            f"We weren't able to create a fit card this time.\n\n"
            f"Here's the listing: {title} — ${price} on {platform}\n\n"
            f"Outfit ideas for this piece:\n{outfit_suggestions}\n\n"
            "Would you like to try again?"
        )

    client = _get_groq_client()

    title = new_item.get("title", "Unknown item")
    price = new_item.get("price", "")
    platform = new_item.get("platform", "a thrift app")
    colors = ", ".join(new_item.get("colors", []))
    style_tags = ", ".join(new_item.get("style_tags", []))

    prompt = (
        "You are a fashion-forward social media creator who posts authentic, excited OOTD content.\n\n"
        f"New thrifted find: {title}"
        + (f", ${price}" if price else "")
        + f" from {platform}.\n"
        f"Colors: {colors}\nStyle: {style_tags}\n\n"
        f"Outfit idea:\n{outfit}\n\n"
        "Write a 2–4 sentence Instagram/TikTok caption for this outfit. Rules:\n"
        "- Sound like a real person, not a brand — casual, excited, specific\n"
        "- Mention the item name, price, and platform each exactly once, woven in naturally\n"
        "- Describe the outfit vibe in concrete terms (not just 'cute' or 'fun')\n"
        "- No hashtags. No emojis unless they feel genuinely natural.\n"
        "Return only the caption text."
    )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.95,
    )

    return response.choices[0].message.content

# tests/test_tools.py
from tools import search_listings, suggest_outfit, create_fit_card

SAMPLE_ITEM = {
    "title": "Vintage Levi's Denim Jacket",
    "category": "outerwear",
    "colors": ["blue", "white"],
    "style_tags": ["vintage", "casual", "denim"],
    "description": "Classic Levi's trucker jacket, lightly worn.",
    "price": 35.0,
    "platform": "depop",
}

def test_search_returns_results():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    assert isinstance(results, list)
    assert len(results) > 0

def test_search_empty_results():
    results = search_listings("designer ballgown", size="XXS", max_price=5)
    assert results == []   # empty list, no exception

def test_search_price_filter():
    results = search_listings("jacket", size=None, max_price=10)
    assert all(item["price"] <= 10 for item in results)

def test_search_size_none_does_not_filter_by_size():
    # size=None should return more results than a restrictive size filter
    results_no_size = search_listings("jacket", size=None, max_price=None)
    results_size = search_listings("jacket", size="XXXL", max_price=None)
    assert len(results_no_size) >= len(results_size)

def test_search_price_none_does_not_filter_by_price():
    # max_price=None should return more results than a very low price ceiling
    results_no_price = search_listings("jacket", size=None, max_price=None)
    results_price = search_listings("jacket", size=None, max_price=1)
    assert len(results_no_price) >= len(results_price)

def test_search_both_none_returns_results():
    # With both filters off, keyword scoring alone should still match items
    results = search_listings("vintage tee", size=None, max_price=None)
    assert isinstance(results, list)
    assert len(results) > 0

def test_search_empty_description_returns_empty():
    # Empty description produces no keywords, so every item scores 0 and is dropped
    results = search_listings("", size=None, max_price=None)
    assert results == []

def test_suggest_outfit_empty_wardrobe():
    # Empty wardrobe should produce general styling advice, not raise
    result = suggest_outfit(SAMPLE_ITEM, wardrobe={"items": []})
    assert isinstance(result, str)
    assert len(result) > 0

def test_create_fit_card_empty_outfit_string():
    # Empty outfit triggers the fallback path — returns an error message string, not an exception
    result = create_fit_card("", SAMPLE_ITEM)
    assert isinstance(result, str)
    assert len(result) > 0

def test_create_fit_card_whitespace_outfit_string():
    # Whitespace-only outfit also triggers the fallback (outfit.strip() is falsy)
    result = create_fit_card("   ", SAMPLE_ITEM)
    assert isinstance(result, str)
    assert len(result) > 0
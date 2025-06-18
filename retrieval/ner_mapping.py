NER_DOMAINS_SET = {
    "electronics",
    "restaurants",
    "groceries",
    "pharmacies",
    "sports",
    "fashion",
    "home_garden",
}

CATEGORY_MAPPING = {
    # -- Electronics
    "appliances": "electronics",
    "entertainment": "electronics",
    "gaming": "electronics",
    # -- Restaurants
    "food": "restaurants",
    # -- Pharmacies
    "beauty": "pharmacies",
    "health": "pharmacies",
    "health & beauty": "pharmacies",
    "health & nutrition": "pharmacies",
    "kids": "pharmacies",
    # "stationary": "groceries",
    # -- Home Garden
    "arts & crafts": "home_garden",
    "home": "home_garden",
    "home & garden": "home_garden",
    "home decor": "home_garden",
    "home essentials": "home_garden",
    # -- Groceries
    "pet care": "groceries",
    # -- Sports
    "toys & games": "sports",
    "toys and games": "sports",
    "unsupported": "unsupported",
}


def _map_category(category):
    mapped_category = CATEGORY_MAPPING.get(category)
    if mapped_category:
        return mapped_category
    return category


def find_ner_domain(item):
    vendor_kind = item["category"]
    shopping_category = item["shoppingCategory"]["en"].strip()
    shopping_subcategory = item["shoppingSubcategory"]["en"].strip()

    # Shopping subcategory match?
    category = _map_category(shopping_subcategory)
    if category in NER_DOMAINS_SET:
        return category

    # Shopping category match?
    category = _map_category(shopping_category)
    if category in NER_DOMAINS_SET:
        return category
    # Vendor kind match?
    category = _map_category(vendor_kind)
    if category in NER_DOMAINS_SET or category == "unsupported":
        return category

    # Failed!
    return None

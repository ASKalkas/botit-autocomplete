"""
A Data reader from Items.
A reader does provide:
    * Read data from items endpoint, in various formats: Items objects, raw dicts or pandas dataframe.
    * Update and read items from a cache (dump file).
"""

import json
import os
import pickle
import re
from collections import namedtuple
from itertools import groupby
from os.path import join
from time import time
from typing import List, Dict, Tuple

from dotenv import load_dotenv

from retrieval.config import CACHE_DIR
from retrieval.database import Item
from retrieval.database import ItemsDataSource
from retrieval.database.categories_translator import CategoriesTranslator
from retrieval.ner_mapping import find_ner_domain

load_dotenv()

VendorSplit = namedtuple(
    "VendorSplit",
    [
        "category",
        "vendor_name",
        "vendor_id",
        "start",
        "end",
    ],
)


def read_stock_cache():
    """Reads stock cache from cache dir."""
    if not os.path.exists(join(CACHE_DIR, "stock_cache.pkl")):
        return []

    with open(join(CACHE_DIR, "stock_cache.pkl"), "rb") as f:
        stock_cache = pickle.load(f)
        return stock_cache


def get_dict_value(dictionary, key, default):
    """
    Return value of a given key in a given dict.
    if key does not exist or has a value of None, the passed default will be returned.
    """
    value = dictionary.get(key)
    if value is None:
        return default
    return value


def sort_and_calculate_splits(items):
    """
    Sort items by (category -> vendor -> name), group them by (category -> vendor) and format the splits list

    Returns: sorted items, split list
    """
    splits = []

    # sort items by category and vendor
    sorting_key = lambda item: (
        str(item["category"]),
        str(item["vendor_name"]["en"]),
        str(item["name"]["en"]),
    )

    items = sorted(items, key=sorting_key)

    idx = 0
    for category, c_items in groupby(items, key=lambda item: item["category"]):
        for vendor, v_items in groupby(
            c_items, key=lambda item: (item["vendor_name"], item["vendor_id"])
        ):
            v_items = list(v_items)

            vendor_name, vendor_id = vendor
            vendor_split = VendorSplit(
                category=category,
                vendor_name=vendor_name,
                vendor_id=vendor_id,
                start=idx,
                end=idx + len(v_items),
            )
            idx += len(v_items)
            splits.append(vendor_split)

    return items, splits


class ItemsReader:
    """
    Interfaces items endpoint, providing items data as raw dicts, items_retrieval.Item objects or pandas dataframe.
    along with their vendor splits, where a vendor split is tuple containing (category, vendor, start_idx, end_idx)
    """

    def __init__(self, items_data_source: ItemsDataSource):
        """
        Setup a database client and cache directory.

        Args:
            data_source
        """
        self.data_source = items_data_source
        self.cache_dir = CACHE_DIR
        self.translator = CategoriesTranslator()

    def _write_cache(self, items):
        """
        Write items and splits into a cache file.

        Args:
            items (list[dict]): items list
            splits (list[VendorSplit]): vendor splits

        Returns:
            None
        """
        # Create Cache dir if not exist
        if not os.path.isdir(self.cache_dir):
            os.mkdir(self.cache_dir)

        with open(join(self.cache_dir, "items"), "wb") as f:
            pickle.dump(items, f)

    def _read_cache(self):
        """
        Read items and splits from cache file.

        Returns:
            items (list[dict]): items list
        """
        with open(join(self.cache_dir, "items"), "rb") as f:
            data = pickle.load(f)

        return data

    def _write_items_stock_cache(self, items):
        """
        Write tuples of item ids and list of the available areas.

        Args:
            items (list[Item]): items list
        Returns:
            None
        """

        stock_cache = [(item.id, item.in_stock_areas) for item in items]
        # Create Cache dir if not exist
        if not os.path.isdir(self.cache_dir):
            os.mkdir(self.cache_dir)

        with open(join(self.cache_dir, "stock_cache.pkl"), "wb") as f:
            pickle.dump(stock_cache, f)

    def _fetch_data(
        self, cached=False, live_vendors_only=False, live_vendors_only_testing=False
    ) -> Tuple[List[Dict], bool]:
        """
        Fetch items data from database.

        if the fetch operation failed, or cached argument is True, it will attempt to read
         previously cached data from self.cache_dir.
        Args:
            cached(bool): Use cached data.
            live_vendors_only(bool): Filter by live vendors.
            live_vendors_only_testing(bool): Filter by live vendors during db testing.
        Returns:
            Tuple containing a list of documents and a boolean indicating whether the data is from cache.
        """
        is_from_cache = False
        t_0 = time()
        if cached:
            data = self._read_cache()
            is_from_cache = True
        else:
            try:
                data = self.data_source.fetch_items(
                    live_vendors_only=live_vendors_only,
                    live_vendors_only_testing=live_vendors_only_testing,
                )
                self._write_cache(data)

            except Exception as e:
                data = []

            if not data:  # got empty response or failure
                data = self._read_cache()
                is_from_cache = True

        return data, is_from_cache

    def _parse_raw_item(self, item):
        """
        Extract items relevant attributes, set their defaults and unify their structure

        Args:
            item (dict): raw item dictionary as received from the db client.

        Returns:
             A dictionary with parsed relevant attributes with missing values
              substituted by defaults, None values and empty strings are dropped as well.
        """

        # Default empty values
        DEFAULT_ITERABLE_VALUE = lambda: {"en": [], "ar": []}
        DEFAULT_STRING_VALUE = lambda: {"en": "", "ar": ""}
        DEFAULT_ATTR_VALUE = lambda: {"en": {}, "ar": {}}

        # Get outer level values.
        item_attributes = {
            "id": item["_id"],  # a must-have, no default
            "category": item["kind"],
            "vendor_name": item["vendor"]["name"],
            "vendor_id": item["vendor"]["id"],
            "is_new_arrival": get_dict_value(item, "newArrival", False),
            "db_collection": get_dict_value(item, "db_collection", "Items"),
            "available_areas": item.get("available_areas", []),
            "in_stock_areas": item.get("in_stock_areas", []),
            "variants": item.get("variants", []),
        }
        # -- parse item price
        try:
            item_attributes["price"] = float(item["price"])
        except:
            item_attributes["price"] = 0.0

        # -- name and title
        item_name = DEFAULT_STRING_VALUE()
        attr_value = get_dict_value(item, "name", {})
        item_name.update(attr_value)
        item_attributes["name"] = item_name

        # Enforce type casting
        item_attributes["name"]["en"] = str(item_attributes["name"]["en"])
        item_attributes["name"]["ar"] = str(item_attributes["name"]["ar"])

        item_attributes["title"] = item_name.copy()

        # # -- parse tags_gsw
        tags_gsw = DEFAULT_ITERABLE_VALUE()
        en_tags_gsw = get_dict_value(item, "tags_gsw", [])
        if en_tags_gsw:
            tags_gsw_en_splits = [
                en_tag.strip() for en_tag in re.split(r"[,\n]", en_tags_gsw)
            ]
            # Split on : then take the last value for example material: stainless steel -> (stainless steel)
            tags_gsw_en_splits = [re.split(r":", v)[-1] for v in tags_gsw_en_splits]
            # Remove any numbering scheme in the beginning of tag 1. , 2- , 3), -
            tags_gsw_en_splits = [
                re.sub(r"\d+\)|\d+-|-|\d+\.\s*", "", v).strip()
                for v in tags_gsw_en_splits
            ]
            # keep only tags with text and neglect empty strings
            tags_gsw["en"] = [
                tag_split for tag_split in tags_gsw_en_splits if tag_split
            ]
            tags_gsw["ar"] = [self.translator.translate(tag) for tag in tags_gsw["en"]]
        item_attributes["tags_gsw"] = tags_gsw

        # -- parse tags_dsw
        tags_dsw = DEFAULT_ITERABLE_VALUE()
        attr_value = get_dict_value(item, "tags_dsw", {})
        for lang in ["en", "ar"]:
            if not attr_value.get(lang):
                continue
            # # Split on commas, new lines
            splits = re.split(r"[,،\n]", str(attr_value[lang]))
            # Split on : then take the last value for example material: stainless steel -> (stainless steel)
            splits = [re.split(r":", v)[-1] for v in splits]
            # Remove any numbering scheme in the beginning of tag 1. , 2- , 3), -
            splits = [re.sub(r"\d+\)|\d+-|-|\d+\.\s*", "", v).strip() for v in splits]
            tags_dsw[lang].extend([value for value in splits if value])

        item_attributes["tags_dsw"] = tags_dsw

        # -- reshape categories
        categories = DEFAULT_ITERABLE_VALUE()
        for entry in get_dict_value(item, "categories", []):
            for lang in ["en", "ar"]:
                if entry.get(lang) is None:
                    continue
                categories[lang].append(entry[lang])
        item_attributes["categories"] = categories

        # -- original synonyms list (provided by the vendors)
        synonyms = DEFAULT_ITERABLE_VALUE()
        synonyms_value = get_dict_value(item, "synonyms", {})
        for lang in ["en", "ar"]:
            if not synonyms_value.get(lang):
                continue
            synonyms[lang].extend(synonyms_value[lang])

        item_attributes["vendor_synonyms"] = synonyms

        # -----------------------------------------------------
        # Parse other attributes are nested under item["data"]
        item_data = get_dict_value(item, "data", {})

        # -- override title with processed name if exist
        processed_name = DEFAULT_STRING_VALUE()
        attr_value = get_dict_value(item_data, "pName", {})
        processed_name.update(attr_value)

        for lang in ["en", "ar"]:
            if processed_name[lang]:
                item_attributes["title"][lang] = processed_name[lang]

        # -- parse single valued attributes, that has both languages
        for key in [
            "shoppingCategory",
            "shoppingSubcategory",
            "itemCategory",
            "itemSubcategory",
        ]:
            value = DEFAULT_STRING_VALUE()
            attr_value = get_dict_value(item_data, key, {})
            value.update(attr_value)

            if not value["ar"]:
                value["ar"] = self.translator.translate(value["en"])

            item_attributes[key] = value

        # get iterable values that already grouped by language
        for key in [
            "keywords",
            "pKeywords",
            "synonyms",
        ]:
            value = DEFAULT_ITERABLE_VALUE()
            attr_value = get_dict_value(item_data, key, {})
            for lang in ["en", "ar"]:
                if not attr_value.get(lang):
                    continue
                # Remove any numbering scheme in the beginning of tag 1. , 2- , 3), -
                attr_value[lang] = [
                    re.sub(r"\d+\)|\d+-|-|\d+\.\s*", "", keyword)
                    for keyword in attr_value[lang]
                    if keyword
                ]
                value[lang].extend(attr_value[lang])

            item_attributes[key] = value
        # if item has no pKeywords but has keywords, fall-back to keywords
        # and override pKeywords with keywords
        if not item_attributes["pKeywords"]["en"] and item_attributes["keywords"]["en"]:
            item_attributes["pKeywords"] = item_attributes["keywords"]

        # -----------------------------------------------------
        # Get key_attributes
        item_attributes["key_attributes"] = {}
        key_attributes = get_dict_value(item_data, "keyAttrs", {})
        for key in key_attributes:
            value = DEFAULT_ITERABLE_VALUE()
            attr_value = get_dict_value(key_attributes, key, {})
            value.update(attr_value)

            item_attributes["key_attributes"][key] = value
        try:
            item_attributes = self._drop_duplicates_nones_and_empty_str(item_attributes)
        except:
            pass
        item_attributes["ner_domain"] = find_ner_domain(item_attributes)
        # if "ai_attributes" in item["data"].keys():
        # --------------------------------------------------------
        # Extract GPT attributes and Variants
        item_attributes["ai_attributes"] = DEFAULT_ATTR_VALUE()
        attrs_value_list = get_dict_value(item_data, "ai_attributes", None)

        if attrs_value_list:
            for lang in ["en", "ar"]:
                variations_attrs = (
                    []
                )  # list of dicts each dict has on variation attributes
                for index, attr_value in enumerate(attrs_value_list):
                    # Skip if no attributes
                    try:
                        if attr_value[lang] is None:
                            continue

                    except Exception as exc:

                        # If an error occurred while parsing attributes, drop the corresponding variant
                        if index < len(item_attributes["variants"]):
                            del item_attributes["variants"][index]

                        continue
                    # Extract each variation attributes and append to list of variations attributes
                    if type(attr_value[lang]) is str and attr_value.get(
                        "variation_id", None
                    ):
                        variations_attrs.append(
                            {
                                attr_value.get(
                                    "variation_id"
                                ): self.extract_attrs_by_regex(
                                    attributes=attr_value[lang]
                                )
                            }
                        )
                item_attributes["ai_attributes"][lang] = variations_attrs

        return item_attributes

    @staticmethod
    def extract_attrs_by_regex(attributes):
        """Extract a dict of attributes using regex

        Args:
            attributes (str): A new line separated string contains gpt attributes

        Returns:
            extracted_attributes (dict): A dict of extracted attributes
        """
        extracted_attributes = {}
        # First step is to split the strings on new lines
        splits_on_new_lines = re.split(r"[\n]", attributes)

        # Loop on the list of splits and extract values after :
        for split in splits_on_new_lines:
            # If no : separator then discard this attribute
            if ":" not in split:
                continue
            # before ':' is the key and after ':' is the list of values
            attr_name = re.split(r":", split)[0].lower().strip()
            attr_values = [re.split(r":", split)[1].lower().strip()]

            # replace space with _ for avoiding importing problems in chatito
            attr_name = re.sub(" ", "_", attr_name)

            # convert values separated by , into a list
            for value in attr_values:
                if "," in value:
                    values = value.split(",")
                    attr_values = [attr.strip() for attr in values]
                    # filter empty strings
            extracted_attributes[attr_name] = [val for val in attr_values if val != ""]
        return extracted_attributes

    def _drop_duplicates_nones_and_empty_str(self, value):
        """
        Recursively drop any duplicates, Nones or empty strings
        inside a given value (dict/list)
        """
        value_type = type(value)
        if value is None:
            value = ""
            # raise ValueError("None is not accepted as a field value!")

        elif value_type is str:
            pass

        elif value_type is list:
            # drop None, duplicates and ""
            value = set([x for x in value if x not in [None, ""]])
            value = sorted(list(value))

        elif value_type is dict:
            for k in value:
                value[k] = self._drop_duplicates_nones_and_empty_str(value[k])

        return value

    def _log_skipped_uncategorized_items(self, items):
        """
        Group uncategorized items by vendor, format and write a summary log file.

        Args:
            items:

        """

        skipped_category_triplets = {
            (
                item["category"],
                item["shoppingCategory"]["en"],
                item["shoppingSubcategory"]["en"],
            )
            for item in items
        }
        skipped_category_triplets = [
            {
                "vendor.shopping_category": t[0],
                "item.shopping_category": t[1],
                "item.shopping_subcategory": t[2],
            }
            for t in skipped_category_triplets
        ]

        log = {"category_triplets": skipped_category_triplets, "items": []}

        items.sort(key=lambda item: (item["category"], item["vendor_name"]["en"]))
        for key, group_items in groupby(
            items,
            key=lambda item: (item["category"], item["vendor_name"]["en"]),
        ):
            category, vendor = key
            group_items = list(group_items)

            log["items"].append(
                {
                    "vendor": vendor,
                    "category": category,
                    "count": len(group_items),
                    "items": [
                        {"ID": item["id"], "Name": item["name"]["en"]}
                        for item in group_items
                    ],
                }
            )

        with open(join(self.cache_dir, "skipped_uncategorized_items.json"), "w") as f:
            json.dump(log, f, indent=2)

    def _parse_items_data(
        self,
        cached=False,
        allow_uncategorized_items=False,
        live_vendors_only=False,
        live_vendors_only_testing=False,
    ) -> Tuple[List[Dict], List[VendorSplit], bool]:
        """
        Calls the endpoint and parse the relevant data from the response

        Args:
            cached (bool): If set to True, read cached data.
            allow_uncategorized_items(bool): Return uncategorized items.
            live_vendors_only(bool): Filter by live vendors.
            live_vendors_only_testing(bool): Filter by live vendors during db testing.


        Returns: [items, splits]
            items (list[dict]): items list
            splits (list[VendorSplit]): vendor splits
            is_data_from_cached (bool): set to True when the items were read from the cache
        """

        data, is_data_from_cache = self._fetch_data(
            cached=cached,
            live_vendors_only=live_vendors_only,
            live_vendors_only_testing=live_vendors_only_testing,
        )

        # Parse and normalize items data
        if allow_uncategorized_items:
            items = []
            for index, item in enumerate(data):
                try:
                    parsed_item = self._parse_raw_item(item)
                    items.append(parsed_item)
                except Exception as e:
                    print()

        else:
            items, uncategorized_items = [], []

            for item in data:
                try:
                    parsed_item = self._parse_raw_item(item)
                    # Skip Uncategorized items
                    if parsed_item["ner_domain"] is None:
                        uncategorized_items.append(parsed_item)
                        continue

                    items.append(parsed_item)
                except Exception as e:
                    print()

            if uncategorized_items:
                self._log_skipped_uncategorized_items(uncategorized_items)

        # TODO: Should we care about other fields? safe to drop one of the duplicates?
        items, splits = sort_and_calculate_splits(items)

        return items, splits, is_data_from_cache

    def read_data_as_dicts(
        self, cached=False, allow_uncategorized_items=False
    ) -> Tuple[List[Dict], List[VendorSplit], bool]:
        """
        Get items data in python dict format

        Args:
            cached (bool): if set to True, read cached data.
            allow_uncategorized_items(bool): Return uncategorized items.

        Returns: [items, splits]
            items (list[dict]): items list
            splits (list[VendorSplit]): vendor splits
            is_data_from_cache(bool): True, when data has been read from the cache
        """
        items, splits, is_data_from_cache = self._parse_items_data(
            cached=cached, allow_uncategorized_items=allow_uncategorized_items
        )

        return items, splits, is_data_from_cache

    def read_data_as_items(
        self, cached=False, allow_uncategorized_items=True, variants_list=False
    ) -> Tuple[List[Item], List[VendorSplit], bool]:
        """
        Get items data as items_retrieval.Item objects

        Args:
            cached (bool): if set to True, read cached data.
            allow_uncategorized_items(bool): Return uncategorized items.
            variants_list (bool): Return list of for each variants item.

        Returns: [items, splits]
            items (list[Item]): items list
            splits (list[VendorSplit]): vendor splits
            is_data_from_cache (bool): True, when data has been read from the cache
        """
        items, splits, is_data_from_cache = self._parse_items_data(
            cached=cached,
            allow_uncategorized_items=allow_uncategorized_items,
            live_vendors_only=True,
        )

        items = [Item(**i) for i in items]
        # Assign item's index for formatting results
        for idx, item in enumerate(items):
            item.list_index = idx

        self._write_items_stock_cache(items)
        return items, splits, is_data_from_cache

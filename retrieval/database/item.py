"""
Defining Item, ItemField classes
"""

from collections.abc import Mapping

from itertools import groupby


class ItemField:
    """
    Represent a single item attribute.
    """

    def __init__(self, name, value, index=True, weight=1, group=0):
        """
        Set field attributes

        Args:
            name (str): field name
            value (str|dict|list): field textual content
            index (bool): whether to index this field or not
            weight (int): field weight
            group (int): which group this field should be assigned to.
        """
        self.name = name
        self.value = value
        self.index = index
        self.weight = weight
        self.group = group
        self.is_mapping = isinstance(self.value, Mapping)
        self.is_iterable = self.check_iterable()

    def check_iterable(self):
        """
        Checks if textual content is iterable

        Example: Synonyms : ["en": [A, B, C]]

        Returns (bool)
        """
        if self.is_mapping:  # {"en": ... , "ar": ..}
            return all(
                [isinstance(self.value[language], list) for language in self.value]
            )
        return isinstance(self.value, list)

    def __repr__(self):
        return f"{self.name}: {self.value}"


def item_field_property(name):
    """
    Build a property for a given attribute(ItemField) name,
    with defined setter and getter functions for its value.

    Args:
        name (str): Item's attribute name

    Returns: property
    """

    def set_field_value(self, value):
        self.__dict__[name].value = value

    def get_field_value(self):
        return self.__dict__[name].value

    return property(fget=get_field_value, fset=set_field_value)


class Item:
    """
    Represent a database item.
    """

    list_index = item_field_property("_list_index")
    sim_score = item_field_property("_sim_score")
    id = item_field_property("_id")
    title = item_field_property("_title")
    name = item_field_property("_name")
    price = item_field_property("_price")
    category = item_field_property("_category")
    vendor_name = item_field_property("_vendor_name")
    vendor_id = item_field_property("_vendor_id")
    is_new_arrival = item_field_property("_is_new_arrival")
    synonyms = item_field_property("_synonyms")
    processed_keywords = item_field_property("_processed_keywords")
    categories = item_field_property("_categories")
    shopping_category = item_field_property("_shopping_category")
    shopping_subcategory = item_field_property("_shopping_subcategory")
    item_category = item_field_property("_item_category")
    item_subcategory = item_field_property("_item_subcategory")
    item_tags_gsw = item_field_property("_item_tags_gsw")
    item_tags_dsw = item_field_property("_item_tags_dsw")
    key_attributes = item_field_property("_key_attributes")
    ner_domain = item_field_property("_ner_domain")
    available_areas = item_field_property("_available_areas")
    variants = item_field_property("_variants")
    ai_attributes = item_field_property("_ai_attributes")
    variant_score = item_field_property("_variant_score")
    variant_id = item_field_property("_variant_id")
    in_stock_areas = item_field_property("_in_stock_areas")

    def __init__(
        self,
        name,
        title,
        id,
        price,
        category,
        vendor_name,
        vendor_id,
        is_new_arrival,
        synonyms,
        pKeywords,
        categories,
        key_attributes,
        itemCategory,
        itemSubcategory,
        shoppingCategory,
        shoppingSubcategory,
        tags_gsw,
        tags_dsw,
        ner_domain,
        available_areas,
        in_stock_areas,
        variants=[],
        ai_attributes=[],
        **kwargs,  # Important for easier db doc -> Item instantiation
    ):
        # Non-index-able Fields
        self._variant_id = ItemField(name="List Index", value="", index=False)
        self._variant_score = ItemField(name="Variant Score", value=0, index=False)
        self._list_index = ItemField(name="List Index", value=0, index=False)
        self._sim_score = ItemField(name="Similarity Score", value=0, index=False)
        self._id = ItemField(name="ID", value=id, index=False)
        self._name = ItemField(name="Name", value=name, index=False)
        self._price = ItemField(name="Price", value=price, index=False)
        self._vendor_name = ItemField(
            name="Vendor Name", value=vendor_name, index=False
        )
        self._vendor_id = ItemField(name="Vendor ID", value=vendor_id, index=False)
        self._is_new_arrival = ItemField(
            name="New Arrival", value=is_new_arrival, index=False
        )
        self._key_attributes = ItemField(
            name="Key Attributes", value=key_attributes, index=False, group=0
        )
        self._available_areas = ItemField(
            "Available Areas", available_areas, index=False
        )
        self._in_stock_areas = ItemField("In Stock Areas", in_stock_areas, index=False)
        self._ner_domain = ItemField("NER Domain", ner_domain, index=False)

        # First Group - Title (parsed form of item's name) and alike.
        self._title = ItemField("Title", title)
        self._synonyms = ItemField("Synonyms", synonyms)
        self._processed_keywords = ItemField("Processed Keywords", pKeywords, group=0)
        self._shopping_category = ItemField(
            "Shopping Category", shoppingCategory, group=0
        )
        self._variants = ItemField("Variants", value=variants, index=False)
        self._ai_attributes = ItemField(
            "AI Attributes", value=ai_attributes, index=False
        )
        # Second Group - Attributes
        for attr in key_attributes:
            self.__dict__[f"_{attr}"] = ItemField(
                attr.title(), key_attributes[attr], group=self._key_attributes.group
            )

        # Third Group - Categories
        self._category = ItemField("Category", category, group=0)
        self._categories = ItemField("Categories", categories, group=0)

        self._shopping_subcategory = ItemField(
            name="Shopping Subcategory",
            value=shoppingSubcategory,
            group=0,
        )
        self._item_category = ItemField(
            "Item Category",
            itemCategory,
            group=0,
        )
        self._item_subcategory = ItemField(
            "Item Subcategory",
            itemSubcategory,
            group=0,
        )

        # Fourth Group - Tags
        self._item_tags_gsw = ItemField(
            "Item GSW tags",
            tags_gsw,
            group=0,
        )
        self._item_tags_dsw = ItemField(
            "Item DSW tags",
            tags_dsw,
            group=0,
        )

    def get_groups_ids(self):
        """
        Gets a list of all defined groups.

        Returns:
            list[int]
        """
        groups = set([field.group for field in self.__dict__.values()])

        return sorted(groups)

    def get_grouped_fields(self):
        """
        Gets item fields grouped by their defined groups.

        Examples:
            {
                0: [TitleField, ...],
                1: [ColorField, ...]
            }

        Returns:
            dict[int: list[ItemField]]
        """
        fields = sorted(self.__dict__.values(), key=lambda x: x.group)
        grouped_fields = {
            group_num: [field for field in group if field.index]
            for group_num, group in groupby(fields, key=lambda x: x.group)
        }

        return grouped_fields

    def get_group_docs(self, fields_group, language):
        """
        Gets list of docs/text values for a given group of fields,
        with each doc repeated according to its corresponding field's weight.

        Args:
            fields_group (list[ItemField]): list of fields
            language (str): one of "en" or "ar"

        Returns: list[str]
            cumulative list of fields docs
        """

        group_docs = []  # all fields text to be joined

        # for each item field
        for field in fields_group:
            # skip if not searchable
            if not field.index:
                continue

            # get its textual value
            doc = field.value
            if field.is_mapping:
                doc = doc[language]

            if not field.is_iterable:
                # apply field weight/repetition
                doc = " ".join([doc] * field.weight)
                doc = [doc.strip()]
            else:
                doc = doc * field.weight

            if doc:
                group_docs.append(doc)

        return group_docs

    def to_docs(self, language):
        """
        Gets weighted item docs grouped by the defined groups

        Args:
            language (str): one of "en" or "ar"

        Returns: dict[int: list[str]]

        """
        fields = self.get_grouped_fields()
        docs = {
            key: self.get_group_docs(group, language) for key, group in fields.items()
        }
        # filter category group from repetition
        # category_tokens_set = set()
        # for doc in docs[2]:
        #     category_tokens_set.update(set(token for token in doc.split()))
        # categories_list = list(category_tokens_set)
        # docs[2] = [' '.join(categories_list)]
        return docs

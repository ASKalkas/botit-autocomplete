"""
Configurations for package components.

    * Vectorization params.
    * Indexing params.
    * Logger setup.
"""

import logging
import os
from pathlib import Path
from typing import NamedTuple

from dotenv import load_dotenv

load_dotenv()


# Directories Paths
RETRIEVAL_DIR = Path(__file__).parent
PROJECT_DIR = RETRIEVAL_DIR.parent
CACHE_DIR = RETRIEVAL_DIR / ".cache/"
INDICES_CHECKLIST_FILES = [
    "items_en",
    "items_ar",
    "splits_en",
    "splits_ar",
    "vectorizers_en.dill",
    "vectorizers_ar.dill",
    "attrs_binary_mat_en.npz",
    "attributes_doc_mat_en.npz",
    "attrs_binary_mat_ar.npz",
    "attributes_magnitudes_ar.pkl",
    "attributes_doc_mat_ar.npz",
    "attributes_magnitudes_en.pkl",
    "items_binary_mat_ar.npz",
    "vendor_entities_ar",
    "idf_vectors_ar.pkl",
    "synonyms_dict_ar.pkl",
    "docs_means_ar.pkl",
    "term_doc_matrix_ar.npz",
    "td_matrix_magnitudes_ar.pkl",
    "terms_strings_lengths_max_token_en.pkl",
    "td_matrix_magnitudes_en.pkl",
    "cuisine_entities_en",
    "docs_means_en.pkl",
    "term_doc_matrix_en.npz",
    "items_binary_mat_en.npz",
    "cuisine_entities_ar",
    "terms_strings_lengths_max_token_ar.pkl",
    "area_entities_ar",
    "vendor_entities_en",
    "synonyms_dict_en.pkl",
    "idf_vectors_en.pkl",
    "area_entities_en",
    "exact_matcher_vectorizers_en.dill",
    "exact_matcher_docs_means_en.pkl",
    "exact_matcher_td_matrix_magnitudes_en.pkl",
    "exact_matcher_term_doc_matrix_en.npz",
    "exact_matcher_items_binary_mat_en.npz",
    "exact_matcher_idf_vectors_en.pkl",
    "exact_matcher_vectorizers_ar.dill",
    "exact_matcher_docs_means_ar.pkl",
    "exact_matcher_td_matrix_magnitudes_ar.pkl",
    "exact_matcher_term_doc_matrix_ar.npz",
    "exact_matcher_items_binary_mat_ar.npz",
    "exact_matcher_idf_vectors_ar.pkl",
    "items_indices_mapping.pkl",
    "is_new_arrival_vector.pkl",
    "prices_vector.pkl",
    "ner_domains.pkl",
    "ner_domains_mappings.pkl",
    "available_areas_vectors.pkl",
    "items_names_en.pkl",
    "items_names_ar.pkl",
]
SEARCH_ATTRS_INDICES_CHECKLIST = [
    "attrs_binary_mat_en.npz",
    "attributes_doc_mat_en.npz",
    "attrs_binary_mat_ar.npz",
    "attributes_magnitudes_ar.pkl",
    "attributes_doc_mat_ar.npz",
    "attributes_magnitudes_en.pkl",
]


class Config:
    exact_matcher_cache = [
        "exact_matcher_vectorizers.dill",
        "exact_matcher_docs_means.pkl",
        "exact_matcher_td_matrix_magnitudes.pkl",
        "exact_matcher_term_doc_matrix.npz",
        "exact_matcher_items_binary_mat.npz",
        "exact_matcher_idf_vectors.pkl",
    ]
    formatter_cache = [
        "items_indices_mapping.pkl",
        "is_new_arrival_vector.pkl",
        "prices_vector.pkl",
        "ner_domains.pkl",
        "ner_domains_mappings.pkl",
        "items_names.pkl",
        "available_areas_vectors.pkl",
    ]
    cache_files = [
        "vectorizers.dill",
        "docs_means.pkl",
        "attributes_indices.pkl",
        "terms_strings_lengths_max_token.pkl",
        "td_matrix_magnitudes.pkl",
        "attributes_magnitudes.pkl",
        "term_doc_matrix.npz",
        "attributes_doc_mat.npz",
        "items_binary_mat.npz",
        "attrs_binary_mat.npz",
        "synonyms_dict.pkl",
        "idf_vectors.pkl",
    ]
    attributes_cache_files = [
        "attributes_magnitudes.pkl",
        "attributes_doc_mat.npz",
        "attrs_binary_mat.npz",
    ]
    # Formatter
    similar_ner_domains = {
        "restaurants": ["restaurants", "groceries"],
        "groceries": ["groceries", "restaurants", "pharmacies", "home_garden"],
        "pharmacies": ["pharmacies", "groceries"],
        "electronics": ["electronics", "home_garden"],
    }

    default_key_to_group_mapping = {
        "title": 0,
        "form": 1,
        "modifiers": 1,
        "gender": 1,
        "target_group": 1,  # temp to be group 0
        "color": 1,  # temp to be group 0
        "volume": 1,  # temp to be group 0
        "sport": 1,  # temp in group 0 till new parsing
        "size": 1,
        "units": 1,
        "fashion_style": 1,
        "size_numeric": 1,
        "target_group_numeric": 1,
    }
    items_indexable_field = {
        "Title",
        "Synonyms",
        "Processed Keywords",
        "Shopping Category",
        "Category",
        "Categories",
        "Shopping Subcategory",
        "Item Category",
        "Item Subcategory",
        "Item GSW tags",
        "Item DSW tags",
        "Color",
        "Size",
        "Units",
        "Target_Group",
        "Material",
        "Sport",
        "Size_Numeric",
        "Target_Group_Numeric",
        "Fashion_Style",
    }

    # Keys omitted from fallback query (DEPRECATED)
    keys_omitted_in_fallback = ["weight", "volume", "title"]
    ner_joined_categories = {"flower_gifts": "home_garden"}

    # Index
    group_weights = {
        0: 0.9,  # Title Group
        1: 0.3,  # Attributes Group
        2: 0.8,  # Category Group
        3: 0.95,  # Tags Group
    }

    # Groups normalize flags
    group_is_normalizable = {
        0: False,  # Title Group
        1: False,  # Attributes Group
        2: False,  # Category Group
        3: True,  # Tags Group
    }

    # Formatter
    # To take portion of items in the sorting layer
    vendors_sorting_items_percentage = 0.3
    # constant number to handle rounding operation in vendor sorting
    rounding_weight_value = 8

    omit_out_of_stock_items_from_search_results = True
    spelling_mistakes_augmentations = True
    vowels_augmentations = True
    add_unique_features_to_query = True


class EnglishConfig(Config):
    # Features
    word_features = True
    char_features = True
    ngrams_type_char = "char"
    ngrams_range_word = (1, 1)
    ngrams_range_word_bi_gram = (2, 2)
    ngrams_range_char = (2, 3)
    words_features_mul = 5
    words_bi_gram_features_mul = 3
    char_features_mul = 1

    # IDF
    idf_damping_factor = 1

    # BM25
    bm25_b_config_by_groups = {0: 0.0001, 1: 0.0001, 2: 0.0001, 3: 0.0001}
    bm25_k_config_by_groups = {0: 20, 1: 20, 2: 20, 3: 20}

    # Processing
    word_segment = True
    spelling_neighbours = False

    # Formatting
    similarity_threshold = 0.37

    # norm parameter for partial match in tags group
    tags_group_normalizer_param = 4.7
    # upper bound tags norm
    tags_len_upper_bound = 15
    # tags norm average tokens
    tags_avg_tokens = 3

    # Item analyzer
    # This weight is used for spelling mistakes processed features
    # TODO: Create weights for each augmentation type.
    # Setting removing vowels to 2 solved the burge issue
    processed_features_weight = 4

    # This weight to control the repetition of synonyms features
    synonym_word_feature_weight = 4
    synonym_word_bi_feature_weight = 2
    synonym_char_feature_weight = 1

    # This coefficient to tune query normalization during division by synonyms length
    query_normalize_coefficient = 0.35


class ArabicConfig(Config):
    select_categories = False

    # Features
    word_features = True
    char_features = True
    ngrams_type_char = "char"
    ngrams_range_word = (1, 1)
    ngrams_range_word_bi_gram = None
    ngrams_range_char = (2, 3)
    words_features_mul = 1
    words_bi_gram_features_mul = 1
    char_features_mul = 1

    # BM25
    bm25_b_config_by_groups = {0: 0.99, 1: 0.99, 2: 0.99, 3: 0.99}
    bm25_k_config_by_groups = {0: 1.2, 1: 1.2, 2: 1.2, 3: 1.2}

    # IDF
    idf_damping_factor = 1

    # Formatting
    similarity_threshold = 0.37

    # norm parameter for partial match in tags group
    tags_group_normalizer_param = 4.7
    # upper bound tags norm
    tags_len_upper_bound = 15
    # tags norm average tokens
    tags_avg_tokens = 3

    # Item analyzer
    # This weight used for filtered features repetition
    processed_features_weight = 1

    # This weight to control the repetition of synonyms features
    synonym_word_feature_weight = 4
    synonym_word_bi_feature_weight = 2
    synonym_char_feature_weight = 1

    # This coefficient to tune query normalization during division by synonyms length
    query_normalize_coefficient = 0.45


class ExactMatcherEnConfig(EnglishConfig):
    # Disable all features except for unigrams
    word_features = True
    char_features = False
    spelling_mistakes_augmentations = False
    add_unique_features_to_query = False
    vowels_augmentations = False
    ngrams_type_char = None
    ngrams_range_word_bi_gram = None
    ngrams_range_word = (1, 1)
    ngrams_range_char = None
    words_features_mul = 1
    words_bi_gram_features_mul = 0
    items_indexable_field = {
        "Name",
        "Shopping Category",
        "Shopping Subcategory",
        "Item Category",
        "Item Subcategory",
        "Item GSW tags",
        "Item DSW tags",
    }


class ExactMatcherArConfig(EnglishConfig):
    # Disable all features except for unigrams
    word_features = True
    char_features = False
    spelling_mistakes_augmentations = False
    vowels_augmentations = False
    add_unique_features_to_query = False
    ngrams_range_word_bi_gram = None
    words_bi_gram_features_mul = 0
    items_indexable_field = {
        "Name",
        "Shopping Category",
        "Shopping Subcategory",
        "Item Category",
        "Item Subcategory",
        "Item GSW tags",
        "Item DSW tags",
    }

class Statics(NamedTuple):
    """
    NamedTuple two save static values used in indexer (any strings like dict keys or static values in code to
    make it more abstract and intuitive).
    """

    # Terms id
    terms_group: int = 0
    # Attributes id
    attributes_group: int = 1
    # Title key of a query object
    title_key: str = "title"
    # Title key of an Item object
    items_title_key: str = "_title"

    # Key of tuple that contains the range which within lies a query synonyms
    query_synonyms_range: str = "range"
    # Query synonyms lower bound index in range dict
    synonyms_lower_bound: int = 0
    # Query synonyms upper bound index in range dict
    synonyms_upper_bound: int = 1
    # Cache types
    redis: str = "redis"
    disk: str = "disk"

    # Languages
    en: str = "en"
    ar: str = "ar"

    # Indexers Types
    items_indexer: str = "Items Indexer"
    exact_matcher: str = "Exact Matcher"
    syntactic_indexer: str = "Syntactic Indexer"
    # Search Server operational modes
    STANDALONE: str = "STANDALONE"  # Retrieves items from db
    DATA_UPDATER: str = "DATA UPDATER"  # Read cached indices

    # Formatter constants
    highly_relevant_mask_threshold = 0.75
    relevant_search_score_threshold = 0.4
    maximum_number_of_items_for_averaging = 10
    price_margin_percentage = 0.15
    name_attribute = "name"
    vendor_name_attribute = "vendor"
    vendor_id_attribute = "vendor_id"
    dummy_value = -1

def get_config(language):
    if language == "ar":
        return ArabicConfig()
    else:
        return EnglishConfig()

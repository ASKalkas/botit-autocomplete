import json
import os
from pathlib import Path
from typing import List, Dict

from dotenv import load_dotenv

from retrieval.config import PROJECT_DIR
from retrieval.ner_mapping import NER_DOMAINS_SET

load_dotenv()

class ItemsDataSource:
    """
    Abstract class for interfacing an items' data source.
    """

    name = None

    def fetch_items(self, live_vendors_only=False, live_vendors_only_testing=False):
        raise NotImplementedError

    def update_items(self, items, language):
        raise NotImplementedError
import dataclasses
from dataclasses import dataclass

import json
from typing import List, Optional

@dataclass
class Author:
    name: str

@dataclass
class Metric:
    citations: int
    downloads: Optional[int] = None

@dataclass
class Article:
    title: str
    DOI: str
    authors: List[Author]
    metrics: Metric

    def __hash__(self):
        return hash(self.DOI)

    def __eq__(self, other):
        return self.DOI == other.DOI

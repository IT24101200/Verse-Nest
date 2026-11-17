# -*- coding: utf-8 -*-
"""
VerseNest Originals — Complete 200 Verified Genuine Sinhala Songs Expansion Dataset
Aggregates all 8 batches across 4 distinct eras:
- Era 1 (1940s–1970s): Batch 1 & 2 (50 Songs)
- Era 2 (1980s–1990s): Batch 3 & 4 (50 Songs)
- Era 3 (2000s–2010s): Batch 5 & 6 (50 Songs)
- Era 4 (2020s–2026): Batch 7 & 8 (50 Songs)
"""

from dataset_batch1 import BATCH_1
from dataset_batch2 import BATCH_2
from dataset_batch3 import BATCH_3
from dataset_batch4 import BATCH_4
from dataset_batch5 import BATCH_5
from dataset_batch6 import BATCH_6
from dataset_batch7 import BATCH_7
from dataset_batch8 import BATCH_8

EXPANSION_BATCHES = [
    BATCH_1,
    BATCH_2,
    BATCH_3,
    BATCH_4,
    BATCH_5,
    BATCH_6,
    BATCH_7,
    BATCH_8
]

ALL_200_SONGS = (
    BATCH_1 +
    BATCH_2 +
    BATCH_3 +
    BATCH_4 +
    BATCH_5 +
    BATCH_6 +
    BATCH_7 +
    BATCH_8
)

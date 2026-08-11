"""Column name mapping module."""

import re
from typing import Optional

from app.config import ALL_EXPECTED_COLUMNS, COLUMN_SYNONYMS


def map_columns(raw_headers: list[str]) -> dict[str, Optional[str]]:
    """Map file headers strictly."""
    mapping: dict[str, Optional[str]] = {col: None for col in ALL_EXPECTED_COLUMNS}

    for raw_header in raw_headers:
        header_stripped = raw_header.strip()
        if header_stripped in ALL_EXPECTED_COLUMNS:
            mapping[header_stripped] = raw_header

    return mapping

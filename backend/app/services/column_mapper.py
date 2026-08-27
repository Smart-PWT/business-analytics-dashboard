"""maps raw headers"""

import os
from typing import Optional

from app.config import ALL_EXPECTED_COLUMNS, ENABLE_LLM_COLUMN_FALLBACK, GROQ_MODEL


def _exact_match(raw_headers: list[str]) -> dict[str, Optional[str]]:
    mapping: dict[str, Optional[str]] = {col: None for col in ALL_EXPECTED_COLUMNS}
    for raw_header in raw_headers:
        header_stripped = raw_header.strip()
        if header_stripped in ALL_EXPECTED_COLUMNS:
            mapping[header_stripped] = raw_header
    return mapping


def _ask_groq_for_header(schema_column: str, candidate_headers: list[str]) -> Optional[str]:
    """ask llm fallback"""
    if not ENABLE_LLM_COLUMN_FALLBACK:
        return None

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print(f"[column_mapper] No GROQ_API_KEY in environment — leaving '{schema_column}' unmapped")
        return None

    try:
        from groq import Groq

        client = Groq(api_key=api_key)
        options = ", ".join(f'"{h}"' for h in candidate_headers) + ', "none"'
        prompt = (
            "You are matching spreadsheet column headers to a business "
            "transaction schema field. Reply with exactly one of the "
            "given header strings (copied exactly), or 'none' if nothing "
            f"fits.\nSchema field: {schema_column}\n"
            f"Candidate headers: {options}\n"
            "Answer:"
        )
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            # reasoning costs tokens
            max_tokens=500,
            temperature=0,
            reasoning_effort="low",  # keep it cheap
        )
        answer = (response.choices[0].message.content or "").strip().strip('"')

        if answer in candidate_headers:
            print(f"[column_mapper] Groq matched '{schema_column}' -> '{answer}'")
            return answer

        for h in candidate_headers:
            if h.strip().lower() == answer.strip().lower():
                print(f"[column_mapper] Groq matched '{schema_column}' -> '{h}'")
                return h

        print(f"[column_mapper] Groq returned '{answer}' for '{schema_column}', "
              f"not in candidates {candidate_headers} — leaving unmapped")
        return None
    except Exception as exc:
        print(f"[column_mapper] Groq call failed for '{schema_column}': {type(exc).__name__}: {exc}")
        return None


def map_columns(raw_headers: list[str]) -> dict[str, Optional[str]]:
    mapping = _exact_match(raw_headers)

    unmapped_columns = [col for col, raw in mapping.items() if raw is None]
    if not unmapped_columns:
        return mapping

    used_headers = {raw for raw in mapping.values() if raw is not None}
    leftover_headers = [h for h in raw_headers if h not in used_headers]
    if not leftover_headers:
        return mapping

    for col in unmapped_columns:
        if not leftover_headers:
            break
        chosen = _ask_groq_for_header(col, leftover_headers)
        if chosen:
            mapping[col] = chosen
            leftover_headers.remove(chosen)

    return mapping


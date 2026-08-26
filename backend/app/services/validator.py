"""validate data schema"""

from dataclasses import dataclass, field

from app.config import REQUIRED_COLUMNS


@dataclass
class ValidationResult:
    is_valid: bool
    missing_required: list[str] = field(default_factory=list)
    column_mapping: dict[str, str | None] = field(default_factory=dict)
    error_message: str | None = None


def validate_schema(column_mapping: dict[str, str | None]) -> ValidationResult:
    """check required columns"""
    missing_required = [col for col in REQUIRED_COLUMNS if column_mapping.get(col) is None]

    if missing_required:
        return ValidationResult(
            is_valid=False,
            missing_required=missing_required,
            column_mapping=column_mapping,
            error_message=(
                "Upload rejected: could not find matching columns for required "
                f"field(s): {', '.join(missing_required)}. "
                "Please check your file headers or rename them to match one of "
                "the expected names (e.g. 'party_name', 'item_name', 'quantity', "
                "'unit_price', 'total_amount', 'transaction_date')."
            ),
        )

    return ValidationResult(is_valid=True, column_mapping=column_mapping)


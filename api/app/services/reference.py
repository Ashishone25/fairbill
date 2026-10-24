import csv
import os

from pydantic import BaseModel


class ReferencePriceRecord(BaseModel):
    item_key: str
    display_name: str
    category: str
    unit: str
    ceiling_or_reference_price: float
    source: str
    source_url: str
    effective_date: str


def load_reference_prices(
    csv_path: str = "data/reference_prices.csv",
) -> dict[str, ReferencePriceRecord]:
    """
    Loads reference prices from a CSV file into an in-memory dictionary
    indexed by item_key.

    Raises:
        ValueError: if required columns are missing, if duplicate keys are found,
                    or if numerical values cannot be parsed.
    """
    if not os.path.exists(csv_path):
        return {}

    REQUIRED_COLUMNS = {
        "item_key",
        "display_name",
        "category",
        "unit",
        "ceiling_or_reference_price",
        "source",
        "source_url",
        "effective_date",
    }

    index: dict[str, ReferencePriceRecord] = {}

    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        if reader.fieldnames is None:
            raise ValueError("CSV file is empty or missing headers")

        missing_columns = REQUIRED_COLUMNS - set(reader.fieldnames)
        if missing_columns:
            raise ValueError(f"Missing required columns in CSV: {missing_columns}")

        for row_num, row in enumerate(reader, start=2):
            item_key = row["item_key"]
            if item_key in index:
                raise ValueError(
                    f"Duplicate item_key found at row {row_num}: {item_key}"
                )

            try:
                price = float(row["ceiling_or_reference_price"])
            except ValueError:
                raise ValueError(
                    f"Bad number for ceiling_or_reference_price at row {row_num}: "
                    f"'{row['ceiling_or_reference_price']}'"
                )

            record = ReferencePriceRecord(
                item_key=item_key,
                display_name=row["display_name"],
                category=row["category"],
                unit=row["unit"],
                ceiling_or_reference_price=price,
                source=row["source"],
                source_url=row["source_url"],
                effective_date=row["effective_date"],
            )
            index[item_key] = record

    return index

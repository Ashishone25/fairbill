from pathlib import Path

import pytest

from app.services.reference import load_reference_prices


@pytest.fixture
def valid_csv(tmp_path: Path):
    file_path = tmp_path / "valid_prices.csv"
    file_path.write_text(
        "item_key,display_name,category,unit,ceiling_or_reference_price,source,source_url,effective_date\n"
        "item1,Item 1,Cat A,ea,10.5,Source A,http://a.com,2023-01-01\n"
        "item2,Item 2,Cat B,ea,20.0,Source B,http://b.com,2023-01-02\n",
        encoding="utf-8",
    )
    return str(file_path)


@pytest.fixture
def missing_columns_csv(tmp_path: Path):
    file_path = tmp_path / "missing_cols.csv"
    file_path.write_text(
        "item_key,display_name,category,unit\nitem1,Item 1,Cat A,ea\n", encoding="utf-8"
    )
    return str(file_path)


@pytest.fixture
def duplicate_keys_csv(tmp_path: Path):
    file_path = tmp_path / "duplicate_keys.csv"
    file_path.write_text(
        "item_key,display_name,category,unit,ceiling_or_reference_price,source,source_url,effective_date\n"
        "item1,Item 1,Cat A,ea,10.5,Source A,http://a.com,2023-01-01\n"
        "item1,Item 1 Dup,Cat A,ea,15.5,Source A,http://a.com,2023-01-01\n",
        encoding="utf-8",
    )
    return str(file_path)


@pytest.fixture
def bad_numbers_csv(tmp_path: Path):
    file_path = tmp_path / "bad_numbers.csv"
    file_path.write_text(
        "item_key,display_name,category,unit,ceiling_or_reference_price,source,source_url,effective_date\n"
        "item1,Item 1,Cat A,ea,not_a_number,Source A,http://a.com,2023-01-01\n",
        encoding="utf-8",
    )
    return str(file_path)


def test_load_valid_csv(valid_csv):
    prices = load_reference_prices(valid_csv)
    assert len(prices) == 2
    assert "item1" in prices
    assert prices["item1"].ceiling_or_reference_price == 10.5
    assert "item2" in prices
    assert prices["item2"].ceiling_or_reference_price == 20.0


def test_missing_columns(missing_columns_csv):
    with pytest.raises(ValueError, match="Missing required columns in CSV"):
        load_reference_prices(missing_columns_csv)


def test_duplicate_keys(duplicate_keys_csv):
    with pytest.raises(ValueError, match="Duplicate item_key found at row 3"):
        load_reference_prices(duplicate_keys_csv)


def test_bad_numbers(bad_numbers_csv):
    with pytest.raises(
        ValueError, match="Bad number for ceiling_or_reference_price at row 2"
    ):
        load_reference_prices(bad_numbers_csv)


def test_missing_file():
    prices = load_reference_prices("nonexistent_file.csv")
    assert prices == {}

import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from src.clean import run_pipeline
from src.transform import (
    clean_csat,
    clean_dates_and_times,
    normalize_column_names,
    remove_exact_duplicates,
)
from src.utils import canonical_category, stable_customer_key, to_snake_case


class UtilityTests(unittest.TestCase):
    def test_to_snake_case(self) -> None:
        self.assertEqual(
            to_snake_case(" Customer Satisfaction Rating "),
            "customer_satisfaction_rating",
        )

    def test_category_normalization_preserves_missing_values(self) -> None:
        actual = canonical_category(
            pd.Series([" social   media ", None], dtype="string")
        )
        self.assertEqual(actual.iloc[0], "Social Media")
        self.assertTrue(pd.isna(actual.iloc[1]))

    def test_customer_key_is_stable_and_case_insensitive(self) -> None:
        first = stable_customer_key("User@Example.com", " Test User ", 1)
        second = stable_customer_key(" user@example.com ", "test user", 99)
        self.assertEqual(first, second)

    def test_customer_key_distinguishes_different_names(self) -> None:
        first = stable_customer_key("user@example.com", "Alice", 1)
        second = stable_customer_key("user@example.com", "Bob", 2)
        self.assertNotEqual(first, second)

    def test_customer_key_falls_back_when_identity_is_incomplete(self) -> None:
        first = stable_customer_key("User@Example.com", None, 1)
        second = stable_customer_key(None, "Test User", 1)
        self.assertEqual(first, second)


class TransformationTests(unittest.TestCase):
    def test_exact_duplicates_are_removed(self) -> None:
        source = pd.DataFrame({"ticket_id": [1, 1], "value": ["a", "a"]})
        clean, count = remove_exact_duplicates(source)
        self.assertEqual(count, 1)
        self.assertEqual(len(clean), 1)

    def test_fractional_csat_is_flagged_and_removed(self) -> None:
        source = pd.DataFrame({"customer_satisfaction_rating": [2.5, 5, None]})
        clean = clean_csat(source)
        self.assertTrue(clean.loc[0, "dq_invalid_csat"])
        self.assertTrue(pd.isna(clean.loc[0, "customer_satisfaction_rating"]))
        self.assertFalse(clean.loc[1, "dq_invalid_csat"])

    def test_negative_resolution_cycle_is_flagged(self) -> None:
        source = pd.DataFrame(
            {
                "date_of_purchase": ["2021-01-01"],
                "first_response_time": ["2023-06-01 12:00:00"],
                "time_to_resolution": ["2023-06-01 11:00:00"],
            }
        )
        clean = clean_dates_and_times(source)
        self.assertTrue(clean.loc[0, "dq_negative_resolution_cycle"])
        self.assertTrue(pd.isna(clean.loc[0, "resolution_cycle_minutes"]))


class PipelineIntegrationTests(unittest.TestCase):
    def test_pipeline_writes_clean_csv_and_quality_summary(self) -> None:
        raw = pd.DataFrame(
            {
                "Ticket ID": [1],
                "Customer Name": [" Test  User "],
                "Customer Email": ["TEST@example.com"],
                "Customer Age": [30],
                "Customer Gender": ["female"],
                "Product Purchased": ["Phone"],
                "Date of Purchase": ["2021-01-01"],
                "Ticket Type": ["technical issue"],
                "Ticket Subject": ["Setup"],
                "Ticket Description": [" Need   help "],
                "Ticket Status": ["closed"],
                "Resolution": ["Resolved"],
                "Ticket Priority": ["high"],
                "Ticket Channel": ["social media"],
                "First Response Time": ["2023-06-01 10:00:00"],
                "Time to Resolution": ["2023-06-01 11:30:00"],
                "Customer Satisfaction Rating": [2],
            }
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            raw_file = root / "raw.csv"
            output_file = root / "processed" / "clean.csv"
            quality_file = root / "processed" / "quality.json"
            duplicate_file = root / "exceptions" / "duplicates.csv"
            raw.to_csv(raw_file, index=False)

            clean, summary = run_pipeline(
                raw_file=raw_file,
                output_file=output_file,
                quality_file=quality_file,
                duplicate_file=duplicate_file,
            )

            self.assertTrue(output_file.exists())
            self.assertTrue(quality_file.exists())
            self.assertEqual(summary["clean_rows"], 1)
            self.assertEqual(clean.loc[0, "ticket_channel"], "Social Media")
            self.assertEqual(clean.loc[0, "resolution_cycle_minutes"], 90)

            saved_summary = json.loads(quality_file.read_text(encoding="utf-8"))
            self.assertEqual(saved_summary, summary)


if __name__ == "__main__":
    unittest.main()

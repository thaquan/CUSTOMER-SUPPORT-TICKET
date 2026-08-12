import unittest

import pandas as pd

from src.model_utils import (
    attach_dimension_key,
    build_dimension,
)

from src.build_model import (
    build_business_dimensions,
    build_date_dimension,
)

from src.build_model import (
    build_all_dimensions,
    build_business_dimensions,
    build_channel_dimension,
)


class BuildDimensionTests(unittest.TestCase):
    def test_build_dimension_single_attribute(self) -> None:
        source = pd.DataFrame(
            {
                "product_purchased": [
                    "Phone",
                    "Laptop",
                    "Phone",
                ]
            }
        )

        dimension = build_dimension(
            source=source,
            attributes=["product_purchased"],
            key_name="product_key",
        )

        self.assertEqual(len(dimension), 2)
        self.assertEqual(
            dimension["product_purchased"].tolist(),
            ["Laptop", "Phone"],
        )
        self.assertEqual(dimension["product_key"].tolist(), [1, 2])

    def test_build_dimension_multiple_attributes(self) -> None:
        source = pd.DataFrame(
            {
                "ticket_type": [
                    "Technical Issue",
                    "Technical Issue",
                    "Billing Inquiry",
                ],
                "ticket_subject": [
                    "Software Bug",
                    "Software Bug",
                    "Payment Issue",
                ],
            }
        )

        dimension = build_dimension(
            source,
            attributes=["ticket_type", "ticket_subject"],
            key_name="issue_key",
        )

        self.assertEqual(len(dimension), 2)
        self.assertTrue(dimension["issue_key"].is_unique)


class AttachDimensionKeyTests(unittest.TestCase):
    def test_attach_dimension_key_preserves_rows_and_maps_keys(self) -> None:
        source = pd.DataFrame(
            {
                "ticket_id": [1, 2, 3],
                "product_purchased": ["Phone", "Laptop", "Phone"],
            }
        )
        dimension = build_dimension(
            source=source,
            attributes=["product_purchased"],
            key_name="product_key",
        )

        result = attach_dimension_key(
            source=source,
            dimension=dimension,
            attributes=["product_purchased"],
            key_name="product_key",
        )

        self.assertEqual(len(result), 3)
        self.assertFalse(result["product_key"].isna().any())
        self.assertEqual(result["product_key"].tolist(), [2, 1, 2])
        self.assertNotIn("_dimension_match", result.columns)

    def test_attach_dimension_key_rejects_unmatched_rows(self) -> None:
        source = pd.DataFrame(
            {
                "ticket_id": [1, 2],
                "product_purchased": ["Phone", "Unknown Product"],
            }
        )
        dimension = pd.DataFrame(
            {
                "product_key": [1],
                "product_purchased": ["Phone"],
            }
        )

        with self.assertRaisesRegex(ValueError, "could not map"):
            attach_dimension_key(
                source=source,
                dimension=dimension,
                attributes=["product_purchased"],
                key_name="product_key",
            )

    def test_attach_dimension_key_rejects_non_unique_lookup(self) -> None:
        source = pd.DataFrame(
            {
                "ticket_id": [1],
                "product_purchased": ["Phone"],
            }
        )
        invalid_dimension = pd.DataFrame(
            {
                "product_key": [1, 2],
                "product_purchased": ["Phone", "Phone"],
            }
        )

        with self.assertRaises(pd.errors.MergeError):
            attach_dimension_key(
                source=source,
                dimension=invalid_dimension,
                attributes=["product_purchased"],
                key_name="product_key",
            )


class BuildBusinessDimensionTests(unittest.TestCase):
    def test_build_business_dimensions(self) -> None:
        source = pd.DataFrame(
            {
                "ticket_id": [1, 2, 3],
                "product_purchased": ["Phone", "Laptop", "Phone"],
                "ticket_type": [
                    "Technical Issue",
                    "Billing Inquiry",
                    "Technical Issue",
                ],
                "ticket_subject": [
                    "Software Bug",
                    "Payment Issue",
                    "Software Bug",
                ],
                "ticket_channel": ["Email", "Chat", "Email"],
                "ticket_priority": ["High", "Low", "High"],
                "ticket_status": ["Open", "Closed", "Open"],
                "customer_age": [25, 42, 25],
                "customer_gender": ["Female", "Male", "Female"],
                "customer_age_band": ["25-34", "35-44", "25-34"],
            }
        )

        dimensions = build_business_dimensions(source)

        self.assertEqual(len(dimensions["product"]), 2)
        self.assertEqual(len(dimensions["issue"]), 2)
        self.assertEqual(len(dimensions["channel"]), 2)
        self.assertEqual(len(dimensions["priority"]), 2)
        self.assertEqual(len(dimensions["status"]), 2)
        self.assertEqual(len(dimensions["customer_profile"]), 2)

        for dimension in dimensions.values():
            key_column = dimension.columns[0]

            self.assertTrue(dimension[key_column].is_unique)
            self.assertFalse(dimension[key_column].isna().any())

class DateDimensionTests(unittest.TestCase):
    def test_build_date_dimension_creates_continuous_calendar(self) -> None:
        source = pd.DataFrame(
            {
                "date_of_purchase": [
                    "2024-01-01",
                    "2024-01-03",
                ]
            }
        )
        dimension = build_date_dimension(source)

        self.assertEqual(len(dimension), 3)
        self.assertEqual(
            dimension["date_key"].tolist(),
            [
                20240101,
                20240102,
                20240103,
            ],
        )

        middle_date = dimension.iloc[1]
        self.assertEqual(
            middle_date["day_name"], 
            "Tuesday"
        )

        self.assertEqual(
            middle_date["month_name"], 
            "January"
        )

        self.assertEqual(
            middle_date["quarter"], 
            "Q1"
        )

        self.assertEqual(
            middle_date["year_month"], 
            "2024-01"
        )

        self.assertFalse(middle_date["is_weekend"])

    def test_build_date_dimension_rejects_no_valid_dates(self) -> None:
        source = pd.DataFrame(
            {
                "date_of_purchase": [
                    None,
                    "invalid-date",
                ]
            }
        )

        with self.assertRaisesRegex(
            ValueError, 
            "no valid dates",
        ):
            build_date_dimension(source)

if __name__ == "__main__":
    unittest.main()

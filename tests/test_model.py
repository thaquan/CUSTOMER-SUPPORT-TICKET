import unittest

import pandas as pd

from src.model_utils import (
    attach_dimension_key,
    build_dimension,
)

from src.build_model import (
    build_all_dimensions,
    build_business_dimensions,
    build_date_dimension,
    build_fact_ticket,
    build_gold_quality_summary,
)
from src.validate_model import (
    validate_dimension,
    validate_fact_ticket,
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


class FactTicketTests(unittest.TestCase):
    def make_silver_fixture(self) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "ticket_id": [1, 2, 3],
                "product_purchased": [
                    "Phone",
                    "Laptop",
                    "Phone",
                ],
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
                "ticket_channel": [
                    "Email",
                    "Chat",
                    "Email",
                ],
                "ticket_priority": [
                    "High",
                    "Low",
                    "High",
                ],
                "ticket_status": [
                    "Open",
                    "Closed",
                    "Open",
                ],
                "customer_age": [25, 42, 25],
                "customer_gender": [
                    "Female",
                    "Male",
                    "Female",
                ],
                "customer_age_band": [
                    "25-34",
                    "35-44",
                    "25-34",
                ],
                "date_of_purchase": pd.to_datetime(
                    [
                        "2024-01-01",
                        "2024-01-02",
                        "2024-01-03",
                    ]
                ),
                "first_response_at": pd.to_datetime(
                    [
                        "2024-02-01 09:00",
                        "2024-02-02 09:00",
                        "2024-02-03 09:00",
                    ]
                ),
                "resolution_at": pd.to_datetime(
                    [
                        None,
                        "2024-02-02 10:00",
                        None,
                    ]
                ),
                "resolution_cycle_minutes": [
                    None,
                    60.0,
                    None,
                ],
                "customer_satisfaction_rating": [
                    None,
                    4.0,
                    None,
                ],
                "is_closed": [False, True, False],
                "has_csat": [False, True, False],
                "is_low_csat": [False, False, False],
                "dq_invalid_age": [False, False, False],
                "dq_invalid_csat": [False, False, False],
                "dq_invalid_purchase_date": [
                    False,
                    False,
                    False,
                ],
                "dq_invalid_first_response_at": [
                    False,
                    False,
                    False,
                ],
                "dq_invalid_resolution_at": [
                    False,
                    False,
                    False,
                ],
                "dq_negative_resolution_cycle": [
                    False,
                    False,
                    False,
                ],
            }
        )

    def test_build_fact_ticket(self) -> None:
        silver = self.make_silver_fixture()
        dimensions = build_all_dimensions(silver)

        fact = build_fact_ticket(
            silver=silver,
            dimensions=dimensions,
        )

        self.assertEqual(len(fact), 3)
        self.assertTrue(fact["ticket_id"].is_unique)

        foreign_keys = [
            "customer_profile_key",
            "product_key",
            "issue_key",
            "channel_key",
            "priority_key",
            "status_key",
            "purchase_date_key",
        ]

        self.assertFalse(
            fact[foreign_keys]
            .isna()
            .any()
            .any()
        )

        self.assertEqual(
            fact["purchase_date_key"].tolist(),
            [
                20240101,
                20240102,
                20240103,
            ],
        )

        for column in [
            "customer_name",
            "customer_email",
            "customer_key",
            "ticket_description",
            "resolution",
        ]:
            self.assertNotIn(column, fact.columns)

    def test_validate_fact_ticket_rejects_duplicate_ticket_id(self) -> None:
        silver = self.make_silver_fixture()
        dimensions = build_all_dimensions(silver)
        fact = build_fact_ticket(
            silver=silver,
            dimensions=dimensions,
        )

        invalid_fact = fact.copy()
        invalid_fact.loc[1, "ticket_id"] = 1

        with self.assertRaisesRegex(
            ValueError,
            "one row per ticket_id",
        ):
            validate_fact_ticket(
                fact=invalid_fact,
                expected_row_count=3,
            )

    def test_build_gold_quality_summary(self) -> None:
        silver = self.make_silver_fixture()
        dimensions = build_all_dimensions(silver)
        fact = build_fact_ticket(
            silver=silver,
            dimensions=dimensions,
        )

        summary = build_gold_quality_summary(
            silver=silver,
            fact=fact,
            dimensions=dimensions,
        )

        self.assertEqual(summary["silver_rows"], 3)
        self.assertEqual(summary["fact_ticket_rows"], 3)
        self.assertEqual(summary["missing_foreign_keys"], 0)
        self.assertEqual(summary["dimension_count"], 7)


class DimensionValidationTests(unittest.TestCase):
    def test_validate_dimension_rejects_duplicate_grain(self) -> None:
        invalid_dimension = pd.DataFrame(
            {
                "product_key": [1, 2],
                "product_purchased": ["Phone", "Phone"],
            }
        )

        with self.assertRaisesRegex(ValueError, "violates its grain"):
            validate_dimension(
                dimension=invalid_dimension,
                key_name="product_key",
                attributes=["product_purchased"],
            )


if __name__ == "__main__":
    unittest.main()

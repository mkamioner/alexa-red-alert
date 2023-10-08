from copy import deepcopy
from decimal import Decimal
from unittest import TestCase
from unittest.mock import MagicMock, patch

from freezegun import freeze_time
import boto3

from alexa_red_alert.alert import Alert
from alexa_red_alert.alert_category import AlertCategory
from alexa_red_alert.data_table import DataTable
from alexa_red_alert.district import District
from tests import (
    create_data_table,
    create_local_dynamodb_client,
    create_local_dynamodb_table,
    reset_local_dynamodb,
)


class DataTableTest(TestCase):
    dynamodb_client: boto3.client

    @classmethod
    def setUpClass(cls) -> None:
        cls.maxDiff = None
        cls.dynamodb_client = create_local_dynamodb_client()

    def setUp(self) -> None:
        reset_local_dynamodb(self.dynamodb_client)
        create_data_table(self.dynamodb_client)

        self.alert = Alert(
            alert_id="some-alert-id",
            alert_category_id="some-alert-category-id",
            title="some-title",
            locations=["some-location-1", "some-location-2"],
            description="some-description",
        )
        self.districts = [
            District(
                english_name="some-english-name-1",
                code="some-code-1",
                district_id="some-district-id-1",
                area_id="some-area-id-1",
                area_name="some-area-name-1",
                hebrew_name="some-hebrew-name-1",
                migun_time_s=100,
            ),
            District(
                english_name="some-english-name-2",
                code="some-code-2",
                district_id="some-district-id-2",
                area_id="some-area-id-2",
                area_name="some-area-name-2",
                hebrew_name="some-hebrew-name-2",
                migun_time_s=200,
            ),
        ]
        self.alert_category = AlertCategory(
            category_id=42,
            code_name="some-code-name",
            duration_minutes=16,
            label="some-label-1",
            description="some-description-1",
        )
        self.table = create_local_dynamodb_table()
        self.data_table = DataTable(table=self.table, re_alert_at_s=100)

    @patch("alexa_red_alert.data_table.DataTable", autospec=True)
    def test_create_from_table_name(self, mock_data_table: MagicMock) -> None:
        mock_dynamodb_resource = MagicMock()

        actual = DataTable.create_from_table_name(
            table_name="some-table-name",
            dynamodb_resource=mock_dynamodb_resource,
            re_alert_at_s=42,
        )

        self.assertEqual(mock_data_table.return_value, actual)
        mock_dynamodb_resource.Table.assert_called_once_with("some-table-name")
        mock_data_table.assert_called_once_with(
            mock_dynamodb_resource.Table.return_value, 42
        )

    @patch("alexa_red_alert.data_table.DataTable", autospec=True)
    @patch("alexa_red_alert.data_table.boto3.resource", autospec=True)
    def test_create_from_table_name_defaults(
        self, mock_boto3_resource: MagicMock, mock_data_table: MagicMock
    ) -> None:
        actual = DataTable.create_from_table_name()

        self.assertEqual(mock_data_table.return_value, actual)
        mock_boto3_resource.assert_called_once_with(
            "dynamodb", region_name="il-central-1"
        )
        mock_boto3_resource.return_value.Table.assert_called_once_with(
            "alexa-red-alert-data-table"
        )
        mock_data_table.assert_called_once_with(
            mock_boto3_resource.return_value.Table.return_value, 120
        )

    @freeze_time("2020-01-01")
    def test_upsert_alert(self) -> None:
        self.data_table.upsert_alert(
            alert=self.alert,
            districts=self.districts,
            alert_category=self.alert_category,
        )
        expected = [
            {
                "pk": "AREA#some-area-id-1",
                "sk": "DISTRICT#some-district-id-1#CATEGORY#some-code-name",
                "pk1": "DISTRICT#some-district-id-1",
                "sk1": "CATEGORY#some-code-name",
                "alert": {
                    "description": "some-description",
                    "locations": ["some-location-1", "some-location-2"],
                    "title": "some-title",
                    "alert_category_id": "some-alert-category-id",
                    "alert_id": "some-alert-id",
                },
                "district": {
                    "area_name": "some-area-name-1",
                    "code": "some-code-1",
                    "hebrew_name": "some-hebrew-name-1",
                    "district_id": "some-district-id-1",
                    "area_id": "some-area-id-1",
                    "english_name": "some-english-name-1",
                    "migun_time_s": Decimal("100"),
                },
                "created_at_s": Decimal("1577836800"),
                "expires_at_s": Decimal("1577837760"),
                "alert_category": {
                    "description": "some-description-1",
                    "label": "some-label-1",
                    "category_id": Decimal("42"),
                    "duration_minutes": Decimal("16"),
                    "code_name": "some-code-name",
                },
                "re_alert_at_s": Decimal("1577836900"),
            },
            {
                "pk": "AREA#some-area-id-2",
                "sk": "DISTRICT#some-district-id-2#CATEGORY#some-code-name",
                "pk1": "DISTRICT#some-district-id-2",
                "sk1": "CATEGORY#some-code-name",
                "alert": {
                    "description": "some-description",
                    "locations": ["some-location-1", "some-location-2"],
                    "title": "some-title",
                    "alert_category_id": "some-alert-category-id",
                    "alert_id": "some-alert-id",
                },
                "district": {
                    "area_name": "some-area-name-2",
                    "code": "some-code-2",
                    "hebrew_name": "some-hebrew-name-2",
                    "district_id": "some-district-id-2",
                    "area_id": "some-area-id-2",
                    "english_name": "some-english-name-2",
                    "migun_time_s": Decimal("200"),
                },
                "created_at_s": Decimal("1577836800"),
                "expires_at_s": Decimal("1577837760"),
                "alert_category": {
                    "description": "some-description-1",
                    "label": "some-label-1",
                    "category_id": Decimal("42"),
                    "duration_minutes": Decimal("16"),
                    "code_name": "some-code-name",
                },
                "re_alert_at_s": Decimal("1577836900"),
            },
        ]

        actual = self.table.scan()["Items"]

        self.assertCountEqual(expected, actual)

    def test_upsert_alert_already_active_ignored(self) -> None:
        expected_1 = [
            {
                "pk": "AREA#some-area-id-1",
                "sk": "DISTRICT#some-district-id-1#CATEGORY#some-code-name",
                "pk1": "DISTRICT#some-district-id-1",
                "sk1": "CATEGORY#some-code-name",
                "alert": {
                    "description": "some-description",
                    "locations": ["some-location-1", "some-location-2"],
                    "title": "some-title",
                    "alert_category_id": "some-alert-category-id",
                    "alert_id": "some-alert-id",
                },
                "district": {
                    "area_name": "some-area-name-1",
                    "code": "some-code-1",
                    "hebrew_name": "some-hebrew-name-1",
                    "district_id": "some-district-id-1",
                    "area_id": "some-area-id-1",
                    "english_name": "some-english-name-1",
                    "migun_time_s": Decimal("100"),
                },
                "created_at_s": Decimal("1577836800"),
                "expires_at_s": Decimal("1577837760"),
                "alert_category": {
                    "description": "some-description-1",
                    "label": "some-label-1",
                    "category_id": Decimal("42"),
                    "duration_minutes": Decimal("16"),
                    "code_name": "some-code-name",
                },
                "re_alert_at_s": Decimal("1577836900"),
            },
        ]
        expected_2 = [
            expected_1[0],
            {
                "pk": "AREA#some-area-id-2",
                "sk": "DISTRICT#some-district-id-2#CATEGORY#some-code-name",
                "pk1": "DISTRICT#some-district-id-2",
                "sk1": "CATEGORY#some-code-name",
                "alert": {
                    "description": "some-description",
                    "locations": ["some-location-1", "some-location-2"],
                    "title": "some-title",
                    "alert_category_id": "some-alert-category-id",
                    "alert_id": "some-alert-id",
                },
                "district": {
                    "area_name": "some-area-name-2",
                    "code": "some-code-2",
                    "hebrew_name": "some-hebrew-name-2",
                    "district_id": "some-district-id-2",
                    "area_id": "some-area-id-2",
                    "english_name": "some-english-name-2",
                    "migun_time_s": Decimal("200"),
                },
                "created_at_s": Decimal("1577836830"),
                "expires_at_s": Decimal("1577837790"),
                "alert_category": {
                    "description": "some-description-1",
                    "label": "some-label-1",
                    "category_id": Decimal("42"),
                    "duration_minutes": Decimal("16"),
                    "code_name": "some-code-name",
                },
                "re_alert_at_s": Decimal("1577836930"),
            },
        ]
        expected_3 = deepcopy(expected_2)
        for expected in expected_3:
            expected["created_at_s"] = Decimal("1577837100")
            expected["expires_at_s"] = Decimal("1577838060")
            expected["re_alert_at_s"] = Decimal("1577837200")

        with freeze_time("2020-01-01T00:00:00Z"):
            self.data_table.upsert_alert(
                alert=self.alert,
                districts=self.districts[0:1],
                alert_category=self.alert_category,
            )

        actual_1 = self.table.scan()["Items"]

        self.assertCountEqual(expected_1, actual_1)

        with freeze_time("2020-01-01T00:00:30Z"):
            self.data_table.upsert_alert(
                alert=self.alert,
                districts=self.districts,
                alert_category=self.alert_category,
            )

        actual_2 = self.table.scan()["Items"]

        self.assertCountEqual(expected_2, actual_2)

        with freeze_time("2020-01-01T00:05:00Z"):
            self.data_table.upsert_alert(
                alert=self.alert,
                districts=self.districts,
                alert_category=self.alert_category,
            )

        actual_3 = self.table.scan()["Items"]

        self.assertCountEqual(expected_3, actual_3)

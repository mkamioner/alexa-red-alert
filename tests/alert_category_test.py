from unittest import TestCase

from alexa_red_alert.alert_category import AlertCategory, parse_alert_category


class AlertCategoryTest(TestCase):
    def setUp(self) -> None:
        self.maxDiff = None

    def test_parse_alert_category(self) -> None:
        raw = {
            "category": 1,
            "code": "missilealert",
            "duration": 10,
            "label": "Missiles",
            "description1": "Enter the protected space and stay in it for 10 minutes",
            "description2": "",
            "link1": "",
            "link2": "https://www.oref.org.il/12943-en/pakar.aspx",
            "matrixid": 1,
        }
        expected = AlertCategory(
            category_id=1,
            code_name="missilealert",
            duration_minutes=10,
            label="Missiles",
            description="Enter the protected space and stay in it for 10 minutes",
        )

        actual = parse_alert_category(raw)

        self.assertEqual(expected, actual)

from unittest import TestCase

from alexa_red_alert.district import District, parse_district


class DistrictTest(TestCase):
    def setUp(self) -> None:
        self.maxDiff = None

    def test_parse_district(self) -> None:
        raw = {
            "label": "Sapir",
            "value": "91C0EAB7E2C14C370DEDF2B2FFE06635",
            "id": "952",
            "areaid": 29,
            "areaname": "Arava",
            "label_he": "ספיר",
            "migun_time": 180,
        }
        expected = District(
            english_name="Sapir",
            code="91C0EAB7E2C14C370DEDF2B2FFE06635",
            district_id="952",
            area_id="29",
            area_name="Arava",
            hebrew_name="ספיר",
            migun_time_s=180,
        )

        actual = parse_district(raw)

        self.assertEqual(expected, actual)

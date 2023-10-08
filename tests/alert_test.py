from unittest import TestCase

from alexa_red_alert.alert import Alert, parse_alert


class AlertTest(TestCase):
    def setUp(self) -> None:
        self.maxDiff = None

    def test_parse_alert(self) -> None:
        raw = {
            "id": "133412344640000000",
            "cat": "1",
            "title": "ירי רקטות וטילים",
            "data": ["שדרות, איבים, ניר עם"],
            "desc": "היכנסו למרחב המוגן ושהו בו 10 דקות",
        }
        expected = Alert(
            alert_id="133412344640000000",
            alert_category_id="1",
            title="ירי רקטות וטילים",
            locations=["שדרות, איבים, ניר עם"],
            description="היכנסו למרחב המוגן ושהו בו 10 דקות",
        )

        actual = parse_alert(raw)

        self.assertEqual(expected, actual)

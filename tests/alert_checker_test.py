# from unittest import TestCase

# import boto3

# from alexa_red_alert.alert import Alert, parse_alert
# from alexa_red_alert.alert_checker import AlertChecker
# from tests import create_local_dynamodb_client, reset_local_dynamodb


# class AlertCheckerTest(TestCase):
#     dynamodb_client: boto3.client

#     @classmethod
#     def setUpClass(cls) -> None:
#         cls.maxDiff = None
#         cls.dynamodb_client = create_local_dynamodb_client()

#     def setUp(self) -> None:
#         reset_local_dynamodb(self.dynamodb_client)

#         self.alert_checker = AlertChecker()

#     def test_load_metadata(self) -> None:
#         self.alert_checker.load_metadata()
#         alert = parse_alert(
#             {
#                 "id": "133412344640000000",
#                 "cat": "1",
#                 "title": "ירי רקטות וטילים",
#                 "data": ["שדרות, איבים, ניר עם", "כפר עזה", "נחל עוז", "סעד", "עלומים"],
#                 "desc": "היכנסו למרחב המוגן ושהו בו 10 דקות",
#             }
#         )

#         self.alert_checker._save_to_db(alert)

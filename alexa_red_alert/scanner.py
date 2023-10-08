from typing import Any
import os

from alexa_red_alert.alert_checker import AlertChecker
from alexa_red_alert.data_table import DataTable

ALERT_CHECKER = AlertChecker()
DATA_TABLE = DataTable.create_from_table_name(os.environ["DATA_TABLE_NAME"])


def lambda_handler(_: dict[str, Any], __: Any) -> None:
    if not ALERT_CHECKER.metadata_loaded:
        print("Loading metadata...")
        ALERT_CHECKER.load_metadata()

    alert = ALERT_CHECKER.scan()
    if not alert:
        print("No alerts found, exiting")
        return

    print("Alerts found, sending to database")
    districts = ALERT_CHECKER.get_districts(alert)
    print(f"{districts=}")

    alert_category = ALERT_CHECKER.get_alert_category(alert)
    print(f"{alert_category=}")

    DATA_TABLE.upsert_alert(alert, districts, alert_category)
    print("Completed")

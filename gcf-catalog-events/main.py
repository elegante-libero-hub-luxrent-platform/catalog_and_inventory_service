import base64
import json
import logging


def handle_catalog_event(event, context):
    """
    Pub/Sub 触发的 Cloud Function 入口。
    event["data"] 是 base64 编码的 JSON 字符串。
    """
    if "data" not in event:
        logging.warning("No data field in Pub/Sub message")
        return

    try:
        decoded = base64.b64decode(event["data"]).decode("utf-8")
        message = json.loads(decoded)
    except Exception as e:
        logging.error(f"Failed to decode message: {e}")
        logging.error(f"Raw event: {event}")
        return

    logging.info(f"Received catalog event: {json.dumps(message)}")


# utils/pubsub_client.py
from __future__ import annotations

import json
import logging
import os
from typing import Dict, Any

from google.cloud import pubsub_v1


PROJECT_ID = os.getenv("PUBSUB_PROJECT_ID")
TOPIC_ID = os.getenv("PUBSUB_TOPIC_ID")

_publisher: pubsub_v1.PublisherClient | None = None


def _get_publisher() -> pubsub_v1.PublisherClient:
    global _publisher
    if _publisher is None:
        _publisher = pubsub_v1.PublisherClient()
    return _publisher


def publish_event(event_type: str, payload: Dict[str, Any]) -> None:
    """
    {
      "eventType": "...",
      "payload": {...}
    }
    """
    if not PROJECT_ID or not TOPIC_ID:
        logging.warning(
            "PUBSUB_PROJECT_ID or PUBSUB_TOPIC_ID not set; skip publishing event."
        )
        return

    publisher = _get_publisher()
    topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

    message = {
        "eventType": event_type,
        "payload": payload,
    }
    data = json.dumps(message).encode("utf-8")

    future = publisher.publish(topic_path, data=data)
    future.add_done_callback(
        lambda f: logging.info(
            f"Published Pub/Sub event {event_type}, message_id={f.result()}"
        )
    )

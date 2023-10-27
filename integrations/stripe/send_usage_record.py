from datetime import datetime

import requests

from config.config import STRIPE_SECRET_KEY
from config.logger import catch_error
from config.sentry import sentry_sdk


def send_usage_record(subscription_item_id: str, used_minutes_count: int, project_id: str):
    try:
        SEND_USAGE_RECORD_URL = f"https://api.stripe.com/v1/subscription_items/{subscription_item_id}/usage_records"
        usage_record_data = {
            "quantity": used_minutes_count,
            "timestamp": datetime.now().timestamp(),
        }
        auth_with_token = (STRIPE_SECRET_KEY, "")

        response = requests.post(
            url=SEND_USAGE_RECORD_URL,
            data=usage_record_data,
            auth=auth_with_token
        )

        if not response.ok:
            catch_error(
                tag="send_usage_record",
                error=Exception(f"Stripe API Error ({response.status_code}): {response.text}"),
                project_id=project_id
            )

        return response.content
    except Exception as e:
        catch_error(
            tag="send_usage_record",
            error=e,
            project_id=project_id
        )

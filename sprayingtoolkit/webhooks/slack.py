import httpx
import logging

# https://api.slack.com/incoming-webhooks
async def slack(webhook_url, target, sprayer):
    logging.debug("notifying slack webhook of popped account(s)")

    message = {
        "text": f"Popped {len(sprayer.valid_accounts)} {str(sprayer)} accounts! (Target: {target})"
    }

    headers = {"Content-Type": "application/json; charset=UTF-8"}

    await httpx.post(webhook_url, headers=headers, json=message)

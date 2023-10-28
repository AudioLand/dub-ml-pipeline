import sentry_sdk

from config.config import IS_DEV_ENVIRONMENT, SENTRY_DSN

if not IS_DEV_ENVIRONMENT:
    sentry_sdk.init(dsn=SENTRY_DSN)

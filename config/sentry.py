import sentry_sdk

from config.config import SENTRY_DSN

sentry_sdk.init(dsn=SENTRY_DSN)

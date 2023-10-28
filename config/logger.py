import logging

from config.config import IS_DEV_ENVIRONMENT
from config.sentry import sentry_sdk

logging.basicConfig(
    level=logging.ERROR,
    format="[%(asctime)s] - %(levelname)s %(message)s"
)


def catch_error(tag: str, error: Exception, project_id: str):
    from integrations.firebase.firestore_update_project import update_project_status_and_translated_link_by_id

    logging.error(msg=f"({tag}): {str(error)}")

    if not IS_DEV_ENVIRONMENT:
        sentry_sdk.capture_exception(error)

    update_project_status_and_translated_link_by_id(
        project_id=project_id,
        status="translationError",
        translated_file_link=""
    )


if __name__ == "__main__":
    tag = "test_error_tag"
    exception = Exception("some error long message")
    project_id = "some_project_id"
    catch_error(
        tag="test_error_tag",
        error=exception,
        project_id=project_id
    )

import requests

from config.config import UPDATE_PROJECT_URL
from config.logger import catch_error

updating_project_exception = Exception(
    "Error while updating project"
)


def update_project_status_and_translated_link_by_id(
        project_id: str,
        status: str,
        translated_file_link: str
):
    try:
        project_fields_to_update = {
            "id": project_id,
            "status": status,
            "translatedFileLink": translated_file_link
        }

        response = requests.post(
            UPDATE_PROJECT_URL,
            project_fields_to_update,
        )

        if not response.ok:
            catch_error(
                tag="update_project",
                error=Exception(f"Firebase Cloud Function Error ({response.status_code}): {response.text}"),
                project_id=project_id
            )

    except Exception as e:
        catch_error(
            tag="update_project",
            error=e,
            project_id=project_id
        )
        raise updating_project_exception

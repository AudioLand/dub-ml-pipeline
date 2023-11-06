import requests

from config.config import UPDATE_USER_TOKENS_URL
from config.logger import catch_error

updating_user_tokens_exception = Exception(
    "Error while updating user tokens"
)


def update_user_tokens(
    organization_id: str,
    tokens_in_seconds: int,
    project_id: str,
):
    try:
        response = requests.post(
            UPDATE_USER_TOKENS_URL,
            {
                "organization_id": organization_id,
                "tokens": tokens_in_seconds
            },
        )

        if not response.ok:
            catch_error(
                tag="update_user_tokens",
                error=Exception(f"Firebase Cloud Function Error ({response.status_code}): {response.text}"),
                project_id=project_id
            )
            raise updating_user_tokens_exception

    except Exception as e:
        catch_error(
            tag="update_user_tokens",
            error=e,
            project_id=project_id
        )
        raise updating_user_tokens_exception


if __name__ == "__main__":
    organization_id = "ZH7s6QjGGkCFukmNo2SA"
    tokens_in_seconds = 182
    project_id = "3wxihJKadxCzEr8lvqzN"

    update_user_tokens(
        organization_id=organization_id,
        tokens_in_seconds=tokens_in_seconds,
        project_id=project_id
    )

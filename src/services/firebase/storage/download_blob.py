from configs.firebase import bucket
from configs.logger import catch_error, print_info_log
from constants.log_tags import LogTag


def download_blob(
    source_blob_path: str,
    destination_file_path: str,
    project_id: str,
    show_logs: bool = False
):
    try:
        if show_logs:
            print_info_log(
                tag=LogTag.DOWNLOAD_BLOB,
                message=f"File path in bucket: {source_blob_path}"
            )

        blob = bucket.blob(source_blob_path)
        blob.download_to_filename(destination_file_path)

        if show_logs:
            print_info_log(
                tag=LogTag.DOWNLOAD_BLOB,
                message=f"File saved to {destination_file_path}"
            )

    except Exception as e:
        catch_error(
            tag=LogTag.DOWNLOAD_BLOB,
            error=e,
            project_id=project_id
        )

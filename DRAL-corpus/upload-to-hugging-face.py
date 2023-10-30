# See Hugging Face documentation:
# https://huggingface.co/docs/huggingface_hub/v0.18.0.rc0/guides/upload#upload-a-folder

from huggingface_hub import HfApi

api = HfApi()

# Upload the archived version
# api.upload_file(
#     path_or_fileobj="/path/to/DRAL-8.0.tgz",
#     path_in_repo="DRAL-8.0.tgz",
#     repo_id="jonavila/DRAL",
#     repo_type="dataset",
# )

# Upload the unarchived version
api.upload_folder(
    folder_path="/path/to/DRAL-8.0",
    repo_id="jonavila/DRAL",
    path_in_repo=".",
    repo_type="dataset",
)

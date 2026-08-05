from pathlib import Path
import mimetypes

from .logger import logger

class WebsiteUploader:

    def __init__(self,s3_client):
        self.s3 = s3_client

    def upload_directory(self,bucket_name,directory):
        website_dir = Path(directory)

        for file_path in website_dir.rglob("*"):
            if file_path.is_file():
                key = file_path.relative_to(website_dir).as_posix()

                content_type,_=mimetypes.guess_type(file_path)

                extra_args = {}

                if content_type:
                    extra_args["ContentType"] = content_type

                self.s3.upload_file(
                    Filename = str(file_path),
                    Bucket = bucket_name,
                    Key = key,
                    ExtraArgs = extra_args
                )
                logger.info(f"Uploaded {key}")
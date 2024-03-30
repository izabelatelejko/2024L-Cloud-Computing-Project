from functools import cached_property
from pathlib import Path

import yaml
from google.api_core import exceptions
from google.cloud import storage
from pydantic import BaseModel, computed_field


class GcpConfig(BaseModel):
    """GCP project configuration."""

    gcp_project_id: str
    gcp_bucket: str
    region: str
    repository: str
    dataset_id: str
    main_table_name: str
    stg_table_name: str

    @computed_field
    @cached_property
    def bucket_path(self) -> str:
        """Full path to bucket."""
        return f"gs://{self.gcp_bucket}"

    @computed_field
    @cached_property
    def pipeline_root(self) -> str:
        """Pipeline root."""
        return f"{self.bucket_path}/artifacts"

    @computed_field
    @cached_property
    def base_image(self) -> str:
        """Base docker image."""
        return f"{self.region}-docker.pkg.dev/{self.gcp_project_id}/{self.repository}/training"

    @computed_field
    @cached_property
    def main_table_id(self) -> str:
        """Main table ID."""
        return f"{self.gcp_project_id}.{self.dataset_id}.{self.main_table_name}"

    @computed_field
    @cached_property
    def stg_table_id(self) -> str:
        """Staging table ID."""
        return f"{self.gcp_project_id}.{self.dataset_id}.{self.stg_table_name}"


def load_config(config_filename: Path = Path("gcp_config.yml")) -> GcpConfig:
    """Load configuration."""
    return GcpConfig(**yaml.safe_load(config_filename.read_text()))


def check_valid_bucket_name(bucket_name: str) -> bool:
    """Ckeck if bucket name is available."""
    client = storage.Client()
    try:
        exists = client.bucket(bucket_name).exists()
    except exceptions.Forbidden:
        exists = True
    return exists

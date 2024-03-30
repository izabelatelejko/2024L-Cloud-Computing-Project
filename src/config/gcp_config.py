from functools import cached_property
from pathlib import Path

import yaml
from pydantic import BaseModel, computed_field


class GcpConfig(BaseModel):
    """GCP project configuration."""

    gcp_project_id: str
    gcp_bucket: str
    region: str
    repository: str
    main_table_id: str
    stg_table_id: str

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


def load_config(config_filename: Path = Path("gcp_config.yml")) -> GcpConfig:
    """Load configuration."""
    return GcpConfig(**yaml.safe_load(config_filename.read_text()))

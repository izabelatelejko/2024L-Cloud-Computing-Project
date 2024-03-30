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
    def pipeline_root(self) -> str:
        """Pipeline root."""
        return f"gs://{self.gcp_bucket}/artifacts"


def load_config(config_filename: Path = Path("gcp_config.yml")) -> GcpConfig:
    """Load configuration."""
    return GcpConfig(**yaml.safe_load(config_filename.read_text()))

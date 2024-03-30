import os

from jinja2 import Environment, FileSystemLoader, select_autoescape

from src.config.gcp_config import load_config
from src.jinja_utils.template_type import TemplateType


def generate_from_template(template_filename: str, template_type: TemplateType) -> None:
    """Generate terraform scripts with GCP config from jinja2 template."""
    config = load_config().model_dump()
    templates_dir = template_type.value
    out_filename = f"./{templates_dir}/{template_filename[:-3]}"

    jinja_env = Environment(
        loader=FileSystemLoader(searchpath=f"./{templates_dir}/templates"),
        autoescape=select_autoescape(),
    )
    jinja_template = jinja_env.get_template(template_filename)
    out_file = jinja_template.render(config)

    with open(out_filename, "w") as f:
        f.write(out_file)


def generate_all_templates(template_type: TemplateType) -> None:
    """Generate files from all templates for given template type."""
    templates_dir = f"./{template_type.value}/templates"
    for template_filename in os.listdir(templates_dir):
        generate_from_template(template_filename, template_type)

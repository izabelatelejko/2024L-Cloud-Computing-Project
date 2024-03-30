from jinja2 import Environment, FileSystemLoader, select_autoescape

from src.jinja_utils.template_type import TemplateType
from src.config.gcp_config import load_config


def generate_from_template(template_filename, template_type: TemplateType):
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

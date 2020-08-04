from django import template
import os
from django.utils import html
from django.templatetags.static import static

register = template.Library()


@register.simple_tag
def new_relic():
    app_name = os.getenv("NEW_RELIC_APP_NAME", "")
    new_relic_script = ""
    if app_name not in [
        "HC_Portal_Staging",
        "HC_Portal_Production",
        "Production-Terraform-Covid-Portal",
    ]:
        return ""
    elif app_name == "HC_Portal_Staging":
        new_relic_script = "js/new_relic_staging.js"
    else:
        new_relic_script = "js/new_relic_production.js"

    return html.format_html("<script src='{}'></script>", static(new_relic_script))

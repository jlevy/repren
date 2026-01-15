#!/usr/bin/env python

import os
import sys

from jinja2 import Template

# Add the parent directory to the path so we can import repren
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from repren import repren


def generate_readme():
    template_path = os.path.join("docs", "README.template.md")
    with open(template_path) as f:
        template_content = f.read()

    template = Template(template_content)
    rendered = template.render(doc=repren.__doc__)

    with open("README.md", "w") as f:
        f.write(rendered)


if __name__ == "__main__":
    generate_readme()

__all__ = ["get_components"]

import os
import re


COMPONENT_DIR = "./views/assets/js/components"


def assemble_component(filename: str) -> tuple[str, str]:
    fullpath = f"{COMPONENT_DIR}/{filename}"

    if not os.path.isfile(fullpath):
        raise Exception(f"Component '{filename}' not found")

    with open(fullpath, "r", encoding="utf-8") as f:
        raw_content = f.read()


    name       = re.findall(r"<name>(.*?)</name>",             raw_content, re.IGNORECASE | re.DOTALL)
    template   = re.findall(r"<template>(.*?)</template>",     raw_content, re.IGNORECASE | re.DOTALL)
    javascript = re.findall(r"<javascript>(.*?)</javascript>", raw_content, re.IGNORECASE | re.DOTALL)

    if not len(name):
        raise Exception(f"Component '{filename}': could not determine name")

    if not len(template):
        raise Exception(f"Component '{filename}': could not determine template")

    if not len(javascript):
        raise Exception(f"Component '{filename}': could not determine javascript")

    name       = name[0].strip().lower()
    template   = template[0].strip().replace("\n"," ").replace("'",r"\'")
    javascript = javascript[0].strip()

    component = """
        Vue.component('{name}', {{
            template: '{template}',
            {javascript}
        }});
    """.format(name       = name,
               template   = template,
               javascript = javascript)

    return name, component.strip()

def get_components() -> dict[str, str]:
    filenames = [f for f in os.listdir(COMPONENT_DIR) if f.endswith(".vue")]

    components = {}
    for filename in filenames:
        name, component = assemble_component(filename)
        components[name] = component

    return components

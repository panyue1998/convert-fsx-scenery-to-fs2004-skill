#!/usr/bin/env python3
"""Configure ModelConverterX FS2004 compiler paths without GUI automation."""

from __future__ import annotations

import argparse
import xml.etree.ElementTree as ET
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mcx-dir", type=Path, required=True)
    parser.add_argument("--bglcomp", type=Path, required=True)
    parser.add_argument("--makemdl", type=Path, required=True)
    parser.add_argument("--parts-xml", type=Path, required=True)
    args = parser.parse_args()

    for path in (args.bglcomp, args.makemdl, args.parts_xml):
        if not path.is_file():
            parser.error(f"Missing SDK file: {path}")

    config_path = args.mcx_dir / "ModelConverterX.dll.config"
    if config_path.exists():
        tree = ET.parse(config_path)
        root = tree.getroot()
    else:
        root = ET.Element("configuration")
        tree = ET.ElementTree(root)

    sections = root.find("configSections")
    if sections is None:
        sections = ET.Element("configSections")
        root.insert(0, sections)
    group = sections.find("./sectionGroup[@name='userSettings']")
    if group is None:
        group = ET.SubElement(sections, "sectionGroup", {
            "name": "userSettings",
            "type": "System.Configuration.UserSettingsGroup, System.Configuration.ConfigurationManager, Version=8.0.0.0, Culture=neutral, PublicKeyToken=cc7b13ffcd2ddd51",
        })

    section_names = (
        "ASToFra.Utils.FS.FSUtilsSettings",
        "ASToFra.Object.Writer.ObjectWriterSettings",
    )
    section_type = "System.Configuration.ClientSettingsSection, System.Configuration.ConfigurationManager, Version=8.0.0.0, Culture=neutral, PublicKeyToken=cc7b13ffcd2ddd51"
    for name in section_names:
        if group.find(f"./section[@name='{name}']") is None:
            ET.SubElement(group, "section", {
                "name": name,
                "type": section_type,
                "allowExeDefinition": "MachineToLocalUser",
                "requirePermission": "false",
            })

    user_settings = root.find("userSettings")
    if user_settings is None:
        user_settings = ET.SubElement(root, "userSettings")

    values = {
        "ASToFra.Utils.FS.FSUtilsSettings": {"MakeMdlPartsPath": str(args.parts_xml)},
        "ASToFra.Object.Writer.ObjectWriterSettings": {
            "MakeMDLPath": str(args.makemdl),
            "FS2004_BGLCompPath": str(args.bglcomp),
        },
    }
    for section_name, settings in values.items():
        section = user_settings.find(section_name)
        if section is None:
            section = ET.SubElement(user_settings, section_name)
        for setting_name, value in settings.items():
            setting = section.find(f"./setting[@name='{setting_name}']")
            if setting is None:
                setting = ET.SubElement(section, "setting", {"name": setting_name, "serializeAs": "String"})
            value_node = setting.find("value")
            if value_node is None:
                value_node = ET.SubElement(setting, "value")
            value_node.text = value

    ET.indent(tree, space="  ")
    tree.write(config_path, encoding="utf-8", xml_declaration=True)
    print(config_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

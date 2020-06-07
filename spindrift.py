#! /usr/bin/env python3

import sys
import typer
from typing import Union, List
from pydantic import HttpUrl, FilePath
from core.sprayers.owa import OWA


def convert_to_ad_username(name: str, username_format: str, domain: str) -> None:
    first, last = name.strip().split()
    username = username_format.format(first=first, last=last, f=first[:1], l=last[:1])
    print(f"{domain.upper()}\\{username.lower()}" if domain else username.lower())


def main(
    file: Union[FilePath, None],
    target: Union[HttpUrl, str, None],
    domain: Union[str, None],
    format: str = "{f}{last}",
) -> None:

    contents = file if file else sys.stdin

    if target:
        owa = OWA(target)
        domain = owa.netbios_domain

    for line in contents:
        convert_to_ad_username(line, format, domain)


if __name__ == "__main__":
    typer.run(main)

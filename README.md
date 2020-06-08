![](https://img.shields.io/badge/python-v3.7+-BLUE)

# SprayingToolkit

<p align="center">
  <img src="http://38.media.tumblr.com/79d7e2a376cb96fb581b3453070f6229/tumblr_ns5suorqYu1szok8ro1_500.gif" alt="SprayingToolkit"/>
</p>

A collection of Python scripts & utilities that *try* to make password spraying attacks against Lync/S4B, OWA & O365 a lot quicker, less painful and more efficient.

## Brought To You By

<p align="center">
  <a href="https://www.blackhillsinfosec.com/">
    <img src="https://www.blackhillsinfosec.com/wp-content/uploads/2016/03/BHIS-logo-L-300x300.png" alt="blackhillsinfosec"/>
  </a>
</p>

# Tool Overview

## Atomizer ⚛️

A blazing fast password sprayer for Lync, OWA & O365.
Built on Python 3.7+, [HTTPX](https://github.com/encode/httpx) and AsyncIO.

**New:**
now with a RESTful API, HTTP/2 support and O365 account validation!

## Spindrift 💨

Utility script to convert names to active directory usernames or emails according to a specified format.

(e.g `Alice Eve` => `CONTOSO\aeve`, `Alice Eve` => `aeve@contoso.com` )

## Vaporizer 🌬

A port of [@OrOneEqualsOne](https://twitter.com/OrOneEqualsOne)'s [GatherContacts](https://github.com/clr2of8/GatherContacts) Burp extension to an [mitmproxy](https://mitmproxy.org/) add-on with some improvements.

Scrapes Google and/or Bing for LinkedIn profiles, automatically generates emails from the profile names using the specified pattern and performs password sprays in real-time.

## Aerosol 💦

A [mitmproxy](https://mitmproxy.org/) add-on that scrapes all text from the target website and sends it to [AWS Comprehend](https://aws.amazon.com/comprehend/) for analysis to generate custom wordlists for password spraying.

# Installation

Please see the wiki for installation instructions.

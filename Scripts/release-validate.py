#!/usr/bin/env python3
"""Fail-closed release configuration, feed, and archive checks. Standard library only."""
import base64
import hashlib
import os
from pathlib import Path
import plistlib
import re
import sys
import tarfile
import urllib.parse
import xml.etree.ElementTree as ET

NS = {'s': 'http://www.andymatuschak.org/xml-namespaces/sparkle'}

def required(name):
    value = os.environ.get(name, '').strip()
    if not value or any(x in value for x in ('<OWNER>', '<REPOSITORY>', 'example.com', '$(')):
        raise SystemExit(f'Release abgebrochen: {name} fehlt oder enthält Platzhalter.')
    return value

def config():
    for name in ('DEVELOPER_ID_CERTIFICATE_BASE64', 'DEVELOPER_ID_CERTIFICATE_PASSWORD', 'DEVELOPER_ID_IDENTITY', 'APPLE_TEAM_ID', 'NOTARY_KEY_BASE64', 'NOTARY_KEY_ID', 'NOTARY_ISSUER_ID', 'SPARKLE_PRIVATE_KEY', 'SPARKLE_PUBLIC_KEY', 'UPDATE_FEED_URL', 'GH_TOKEN'):
        required(name)
    tag = required('RELEASE_TAG')
    if not re.fullmatch(r'v\d+\.\d+\.\d+', tag):
        raise SystemExit('Nur freigegebene stabile vMAJOR.MINOR.PATCH-Tags sind zulässig.')
    if not required('BUILD_NUMBER').isdigit() or int(required('BUILD_NUMBER')) <= 0:
        raise SystemExit('BUILD_NUMBER muss eine positive, streng steigende Zahl sein.')
    if len(base64.b64decode(required('SPARKLE_PUBLIC_KEY'), validate=True)) != 32:
        raise SystemExit('Der Sparkle-Public-Key muss 32 Bytes enthalten.')
    feed = urllib.parse.urlparse(required('UPDATE_FEED_URL'))
    repo = required('GITHUB_REPOSITORY')
    owner, name = repo.split('/')
    if feed.scheme != 'https' or feed.hostname != owner.lower() + '.github.io' or feed.path != f'/{name}/updates/appcast.xml':
        raise SystemExit('UPDATE_FEED_URL muss auf den GitHub-Pages-Feed dieses Repositorys zeigen.')
    if not required('DEVELOPER_ID_IDENTITY').startswith('Developer ID Application:'):
        raise SystemExit('Keine Developer-ID-Application-Identität konfiguriert.')

def extract(source, destination):
    dest = Path(destination).resolve()
    with tarfile.open(source) as archive:
        for member in archive.getmembers():
            target = (dest / member.name).resolve()
            if not target.is_relative_to(dest) or member.issym() or member.islnk() or not (member.isfile() or member.isdir()):
                raise SystemExit('Unsicheres Pfadobjekt im bisherigen Pages-Archiv.')
        archive.extractall(dest)

def feed(path, archive):
    root = ET.parse(path).getroot()
    items = root.findall('./channel/item')
    expected_build = required('BUILD_NUMBER')
    expected_version = required('RELEASE_TAG')[1:]
    matches = [x for x in items if x.findtext('s:version', namespaces=NS) == expected_build]
    if len(matches) != 1:
        raise SystemExit('Der Appcast enthält nicht genau einen Eintrag für den neuen Build.')
    item = matches[0]
    if item.findtext('s:shortVersionString', namespaces=NS) != expected_version:
        raise SystemExit('Versionsnummer in Appcast und Release weicht ab.')
    enc = item.find('enclosure')
    expected_url = f"https://github.com/{required('GITHUB_REPOSITORY')}/releases/download/{required('RELEASE_TAG')}/{Path(archive).name}"
    if enc is None or enc.get('url') != expected_url or int(enc.get('length', '-1')) != Path(archive).stat().st_size:
        raise SystemExit('Download-URL oder Dateigröße im Appcast stimmt nicht.')
    signature = enc.get('{' + NS['s'] + '}edSignature', '')
    if len(base64.b64decode(signature, validate=True)) != 64:
        raise SystemExit('Appcast enthält keine gültig formatierte EdDSA-Signatur.')
    if item.findtext('s:minimumSystemVersion', namespaces=NS) not in ('14.0', '14.0.0'):
        raise SystemExit('Falsche Mindestversion im Appcast.')
    print(signature)

def previous(path):
    if not Path(path).exists(): return
    for item in ET.parse(path).getroot().findall('./channel/item'):
        version = item.findtext('s:version', namespaces=NS)
        if version is None or not version.isdigit() or int(version) >= int(required('BUILD_NUMBER')):
            raise SystemExit('Build-Version muss strikt über allen bisherigen Builds liegen.')

if __name__ == '__main__':
    command, *args = sys.argv[1:]
    {'config': config, 'extract': extract, 'feed': feed, 'previous': previous}[command](*args)

#!/usr/bin/env python3
"""Verify release metadata, exact bytes, embedded update key and Ed25519 signature."""
import base64, hashlib, importlib.util, json, os, pathlib, plistlib, subprocess, sys, tempfile, zipfile
spec = importlib.util.spec_from_file_location('validate', pathlib.Path(__file__).with_name('release-validate.py'))
validate = importlib.util.module_from_spec(spec); spec.loader.exec_module(validate)
root = pathlib.Path(sys.argv[1])
release = json.loads((root/'release.json').read_text())
assert not release.get('draft') and not release.get('prerelease')
tag = release['tag_name']
assert __import__('re').fullmatch(r'v\d+\.\d+\.\d+', tag)
archive = root / f'Setcrate-{tag[1:]}.zip'
with zipfile.ZipFile(archive) as z:
    info = plistlib.loads(z.read('Setcrate.app/Contents/Info.plist'))
key = os.environ['SPARKLE_PUBLIC_KEY']
assert info['SUPublicEDKey'] == key
assert info['SUFeedURL'] == os.environ['UPDATE_FEED_URL']
assert info['CFBundleShortVersionString'] == tag[1:]
assert info['SUVerifyUpdateBeforeExtraction'] is True
assert info['SUEnableAutomaticChecks'] is True
assert info['SUAutomaticallyUpdate'] is True
checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
assert f'{checksum}  {archive.name}' in (root/'SHA256SUMS').read_text().splitlines()
validate.extract(root/'pages-source.tar.gz', root/'site')
os.environ.update(RELEASE_TAG=tag, BUILD_NUMBER=info['CFBundleVersion'])
validate.feed(root/'site/updates/appcast.xml', archive)
import xml.etree.ElementTree as ET
items = ET.parse(root/'site/updates/appcast.xml').findall('./channel/item')
item = next(x for x in items if x.findtext('s:version', namespaces=validate.NS)==info['CFBundleVersion'])
signature = base64.b64decode(item.find('enclosure').get('{'+validate.NS['s']+'}edSignature'), validate=True)
with tempfile.TemporaryDirectory() as temp:
    p=pathlib.Path(temp)
    (p/'public.der').write_bytes(bytes.fromhex('302a300506032b6570032100')+base64.b64decode(key,validate=True))
    (p/'signature').write_bytes(signature)
    subprocess.run(['openssl','pkeyutl','-verify','-pubin','-keyform','DER','-inkey',str(p/'public.der'),'-rawin','-in',str(archive),'-sigfile',str(p/'signature')],check=True)
print(f'Verified {tag}, build {info["CFBundleVersion"]}: SHA-256, Ed25519, embedded feed and public key.')

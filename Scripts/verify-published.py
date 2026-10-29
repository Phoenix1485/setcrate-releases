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
archives = [root / f'{prefix}-{tag[1:]}.zip' for prefix in ('Rumpel-Maschine', 'Setcrate')]
archives = [p for p in archives if p.is_file()]
assert len(archives) == 1, 'Expected exactly one app archive'
archive = archives[0]
with zipfile.ZipFile(archive) as z:
    roots = [name for name in ('Rumpel Maschine.app', 'Setcrate.app') if name + '/Contents/Info.plist' in z.namelist()]
    assert len(roots) == 1, 'Expected exactly one application bundle'
    info = plistlib.loads(z.read(roots[0] + '/Contents/Info.plist'))
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
def verify_signature(file, signature):
    with tempfile.TemporaryDirectory() as temp:
        p=pathlib.Path(temp)
        (p/'public.der').write_bytes(bytes.fromhex('302a300506032b6570032100')+base64.b64decode(key,validate=True))
        (p/'signature').write_bytes(signature)
        subprocess.run(['openssl','pkeyutl','-verify','-pubin','-keyform','DER','-inkey',str(p/'public.der'),'-rawin','-in',str(file),'-sigfile',str(p/'signature')],check=True)
verify_signature(archive, signature)
if int(info['CFBundleVersion']) >= 8:
    manifest=root/'installer.json'
    verify_signature(manifest, base64.b64decode((root/'installer.sig').read_text().strip(),validate=True))
    m=json.loads(manifest.read_text())
    assert m['version']==tag[1:] and m['build']==info['CFBundleVersion']
    assert m['appSHA256']==checksum
    assert m['filename']==f'Rumpel-Maschine-{tag[1:]}.dmg'
    installer=root/m['filename']
    assert installer.stat().st_size==m['length']
    digest=hashlib.sha256(installer.read_bytes()).hexdigest()
    assert digest==m['sha256']
    assert f'{digest}  {installer.name}' in (root/'SHA256SUMS').read_text().splitlines()
    print('Universal installer verified against its signed manifest and exact app update.')
print(f'Verified {tag}, build {info["CFBundleVersion"]}: SHA-256, Ed25519, embedded feed and public key.')

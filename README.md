# Rumpel Maschine for macOS

Public downloads, release notes and the signed Sparkle update website. The application source is maintained in a separate private repository.

- Website: https://phoenix1485.github.io/setcrate-releases/
- Downloads: https://github.com/Phoenix1485/setcrate-releases/releases
- Update feed: https://phoenix1485.github.io/setcrate-releases/updates/appcast.xml

Requires macOS 14 or later, Intel or Apple Silicon. Download the latest verified app archive from Releases, unzip it and move Rumpel Maschine into Applications. Automatic update checks and downloads are enabled by default; both settings can be changed inside Rumpel Maschine → Settings → Updates. Updates are verified against the app's embedded Ed25519 public key before extraction. Installation waits for active work to finish.

App downloads are Developer-ID signed and notarized by Apple. Rumpel Maschine was previously named Setcrate; existing libraries and update subscriptions are preserved. Audio exports produce only the selected FLAC or WAV files, with embedded metadata.

GitHub Pages restores the latest release's website archive and verifies its SHA-256 checksum, Ed25519 signature and embedded update configuration before publishing. Website changes preserve the latest update feed and historical release notes.

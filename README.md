# Setcrate for macOS

Public downloads, release notes and the signed Sparkle update website. The application source is maintained in a separate private repository.

- Website: https://phoenix1485.github.io/setcrate-releases/
- Downloads: https://github.com/Phoenix1485/setcrate-releases/releases
- Update feed: https://phoenix1485.github.io/setcrate-releases/updates/appcast.xml

Requires macOS 14 or later, Intel or Apple Silicon. Download the latest verified app archive from Releases, unzip it and move Setcrate into Applications. Automatic update checks and downloads are enabled by default; both settings can be changed inside Setcrate → Settings → Updates. Updates are verified against the app's embedded Ed25519 public key before extraction. Installation waits for active work to finish.

The first download is published only after release verification and Apple notarization. Until then, the update feed is intentionally empty.

GitHub Pages restores the latest release's website archive and verifies its SHA-256 checksum, Ed25519 signature and embedded update configuration before publishing. Website changes preserve the latest update feed and historical release notes.

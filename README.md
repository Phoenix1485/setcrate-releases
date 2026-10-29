# Rumpel Maschine for macOS

Public downloads, release notes and the signed Sparkle update website. The application source is maintained in a separate private repository.

- Website: https://phoenix1485.github.io/setcrate-releases/
- Downloads: https://github.com/Phoenix1485/setcrate-releases/releases
- Update feed: https://phoenix1485.github.io/setcrate-releases/updates/appcast.xml

Requires macOS 14 or later. Download the latest `.dmg` universal installer, open “Rumpel Maschine installieren” and choose “In Programme installieren”. One download supports Intel and Apple Silicon. The installer places the app in `/Applications`, registers it for Finder/Spotlight and preserves your library. Quit an existing version before installation.

The Settings gear button shows the installed version, checks for updates and selects System/Light/Dark appearance. Automatic update checks and downloads are enabled by default. The ZIP asset is the Sparkle update archive. App and installer are Developer-ID-signed and Apple-notarized; the installer manifest is signed with the app’s Ed25519 key and checked before the website is deployed. Installation waits for active work to finish.

App downloads are Developer-ID signed and notarized by Apple. Rumpel Maschine was previously named Setcrate; existing libraries and update subscriptions are preserved. Audio exports produce only the selected FLAC or WAV files, with embedded metadata.

GitHub Pages restores the latest release's website archive and verifies its SHA-256 checksum, Ed25519 signature and embedded update configuration before publishing. Website changes preserve the latest update feed and historical release notes.

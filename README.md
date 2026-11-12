# Virtual Jaguar Homebrew tap

Install the standalone Mac app:

```sh
brew tap Provenance-Emu/virtualjaguar
brew trust --cask Provenance-Emu/virtualjaguar/virtualjaguar
brew install --cask Provenance-Emu/virtualjaguar/virtualjaguar
```

The cask uses the notarized universal app from [Virtual Jaguar Releases](https://github.com/libretro/virtualjaguar-libretro/releases).

## Stable cask updates

The tap checks the official repository's latest stable release every six hours.
Maintainers can also run **Sync stable cask** from Actions on the default branch.
Polling keeps the workflow and its GitHub token in the tap. A release may take
until the next scheduled run to appear as a pull request.

The workflow requires a published `vX.Y.Z` release with the universal macOS ZIP
and `SHA256SUMS.txt`. It verifies the downloaded ZIP against the published SHA-256
and, for a new version, validates the app's stapled notarization ticket and both
CPU architectures. An eligible update opens one pull request per version for
manual review and merge. If a maintainer closes an update, subsequent runs leave
it closed. A failed verification leaves the cask untouched.

In **Settings → Actions → General → Workflow permissions**, the tap must allow
**GitHub Actions to create and approve pull requests**. The workflow uses that
setting to create pull requests with the tap's `GITHUB_TOKEN`.

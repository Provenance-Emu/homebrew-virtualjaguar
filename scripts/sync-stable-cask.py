#!/usr/bin/env python3
"""Verify the latest upstream stable app and prepare a cask update."""

import hashlib
import json
from pathlib import Path
import plistlib
import re
import subprocess
from tempfile import TemporaryDirectory

UPSTREAM = "libretro/virtualjaguar-libretro"
CASK = Path("Casks/virtualjaguar.rb")
VERSION = r"(?:0|[1-9][0-9]*)(?:\.(?:0|[1-9][0-9]*)){2}"
CHECKSUM = r"[0-9a-f]{64}"


def run(*args):
    return subprocess.check_output(args, text=True).strip()


def stable_version(release):
    tag = release["tag_name"]
    if (release["draft"] is not False or release["prerelease"] is not False
            or not re.fullmatch("v" + VERSION, tag)):
        raise ValueError(f"Expected a stable vX.Y.Z release, got {tag!r}")
    return tag[1:]


def require_assets(release, *names):
    for name in names:
        matches = [asset for asset in release["assets"] if asset["name"] == name]
        if len(matches) != 1 or matches[0]["state"] != "uploaded" or matches[0]["size"] <= 0:
            raise ValueError(f"Expected exactly one uploaded release asset named {name}")


def verify_checksum(directory, archive):
    entries = []
    for line in (directory / "SHA256SUMS.txt").read_text().splitlines():
        fields = line.split(maxsplit=1)
        if len(fields) == 2 and fields[1].removeprefix("*") == archive:
            entries.append(fields[0])
    if len(entries) != 1 or not re.fullmatch(CHECKSUM, entries[0]):
        raise ValueError(f"Expected exactly one valid SHA-256 entry for {archive}")
    with (directory / archive).open("rb") as downloaded:
        actual = hashlib.file_digest(downloaded, "sha256").hexdigest()
    if actual != entries[0]:
        raise ValueError(f"Downloaded SHA-256 for {archive} is {actual}, expected {entries[0]}")
    return actual


def cask_field(source, name, pattern):
    lines = re.findall(rf"^  {name}\b[^\n]*", source, re.MULTILINE)
    if len(lines) != 1 or not re.fullmatch(rf'  {name} "{pattern}"', lines[0]):
        raise ValueError(f"Expected exactly one cask {name} stanza in the supported format")
    return lines[0]


def main():
    release = json.loads(run("gh", "api", f"repos/{UPSTREAM}/releases/latest"))
    version = stable_version(release)
    tag = f"v{version}"
    archive = f"VirtualJaguar-{version}-macos-universal.zip"
    require_assets(release, archive, "SHA256SUMS.txt")

    source = CASK.read_bytes().decode("utf-8")
    version_line = cask_field(source, "version", VERSION)
    checksum_line = cask_field(source, "sha256", CHECKSUM)
    url_line = (
        f'  url "https://github.com/{UPSTREAM}/releases/download/'
        'v#{version}/VirtualJaguar-#{version}-macos-universal.zip"'
    )
    if source.splitlines().count(url_line) != 1:
        raise ValueError("The cask URL must match the verified release asset")
    current = version_line.split('"')[1]
    if tuple(map(int, version.split("."))) < tuple(map(int, current.split("."))):
        raise ValueError(f"Latest stable {version} is older than the cask version {current}")

    with TemporaryDirectory() as temporary:
        directory = Path(temporary)
        run("gh", "release", "download", tag, "--repo", UPSTREAM, "--dir", temporary,
            "--pattern", archive, "--pattern", "SHA256SUMS.txt")
        checksum = verify_checksum(directory, archive)
        if version == current:
            if checksum_line != f'  sha256 "{checksum}"':
                raise ValueError(f"Upstream replaced the archive for the installed cask version {version}")
            print(f"Cask already matches verified release {tag}.")
            return

        extracted = directory / "extracted"
        run("ditto", "-x", "-k", str(directory / archive), str(extracted))
        app = extracted / "Virtual Jaguar.app"
        run("xcrun", "stapler", "validate", str(app))
        with (app / "Contents/Info.plist").open("rb") as info:
            executable = plistlib.load(info)["CFBundleExecutable"]
        if not executable or executable in {".", ".."} or Path(executable).name != executable:
            raise ValueError("Invalid CFBundleExecutable in the release app")
        architectures = run("lipo", "-archs", str(app / "Contents/MacOS" / executable)).split()
        if not {"arm64", "x86_64"}.issubset(architectures):
            raise ValueError(f"Expected arm64 and x86_64 slices, got {architectures}")

    updated = re.sub(rf"^{re.escape(version_line)}$", f'  version "{version}"',
                     source, flags=re.MULTILINE)
    updated = re.sub(rf"^{re.escape(checksum_line)}$", f'  sha256 "{checksum}"',
                     updated, flags=re.MULTILINE)
    CASK.write_bytes(updated.encode("utf-8"))
    print(f"Prepared {tag} with verified SHA-256 {checksum}.")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as error:
        raise SystemExit(error.output or str(error))
    except ValueError as error:
        raise SystemExit(str(error))

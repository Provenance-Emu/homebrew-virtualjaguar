cask "virtualjaguar" do
  version "3.13.1"
  sha256 "ea91fe2418722a4290dd0feb305d99da9b4c5eb87a8765f47b73adfb16124fa2"

  url "https://github.com/libretro/virtualjaguar-libretro/releases/download/v#{version}/VirtualJaguar-#{version}-macos-universal.zip"
  name "Virtual Jaguar"
  desc "Atari Jaguar and Jaguar CD emulator"
  homepage "https://jaguar.provenance-emu.com/"

  livecheck do
    url :url
    strategy :github_latest
  end

  depends_on macos: :big_sur

  app "Virtual Jaguar.app"

  zap trash: [
    "~/Library/Application Support/VirtualJaguar",
    "~/Library/Saved Application State/io.github.libretro.VirtualJaguar.savedState",
  ]
end

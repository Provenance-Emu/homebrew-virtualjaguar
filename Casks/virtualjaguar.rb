cask "virtualjaguar" do
  version "3.12.0"
  sha256 "6bd9c6fa3264d6c60e524026dff4311eac4db996e6585a0a948ba886ef3a19dc"

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

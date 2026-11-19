cask "virtualjaguar" do
  version "3.13.0"
  sha256 "fda3e22ab0784ccaa21c09e57835eef5e919b03f83ef70577ef625952bc3c83c"

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

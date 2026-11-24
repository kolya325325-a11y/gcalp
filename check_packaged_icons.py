import plistlib
import struct
import sys
import unittest
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent


class PackagedIconTests(unittest.TestCase):
    @unittest.skipUnless(sys.platform == "win32", "Windows executable test")
    def test_windows_executable_contains_calculator_icon(self) -> None:
        import pefile

        icon = (PROJECT_DIR / "assets" / "calculator.ico").read_bytes()
        executable = pefile.PE(str(PROJECT_DIR / "dist" / "Calculator.exe"))
        try:
            resources = {entry.id: entry for entry in executable.DIRECTORY_ENTRY_RESOURCE.entries}
            groups = resources[14].directory.entries
            group_entry = groups[0].directory.entries[0].data.struct
            group = executable.get_data(group_entry.OffsetToData, group_entry.Size)
            icon_resources = {
                entry.id: entry.directory.entries[0].data.struct
                for entry in resources[3].directory.entries
            }

            _, icon_type, count = struct.unpack_from("<HHH", icon)
            self.assertEqual(icon_type, 1)
            self.assertGreater(count, 0)
            self.assertEqual(struct.unpack_from("<HHH", group), (0, 1, count))
            for index in range(count):
                width, height, _, _, _, _, size, offset = struct.unpack_from(
                    "<BBBBHHII", icon, 6 + index * 16
                )
                group_width, group_height, _, _, _, _, group_size, resource_id = (
                    struct.unpack_from("<BBBBHHIH", group, 6 + index * 14)
                )
                resource = icon_resources[resource_id]
                self.assertEqual((group_width, group_height, group_size), (width, height, size))
                self.assertEqual(
                    executable.get_data(resource.OffsetToData, resource.Size),
                    icon[offset : offset + size],
                )
        finally:
            executable.close()

    @unittest.skipUnless(sys.platform == "darwin", "macOS application test")
    def test_macos_bundle_contains_calculator_icon(self) -> None:
        contents = PROJECT_DIR / "dist" / "Calculator.app" / "Contents"
        with (contents / "Info.plist").open("rb") as file:
            info = plistlib.load(file)
        icon_file = info["CFBundleIconFile"]
        self.assertEqual(icon_file, "calculator.icns")
        self.assertEqual(
            (contents / "Resources" / icon_file).read_bytes(),
            (PROJECT_DIR / "assets" / "calculator.icns").read_bytes(),
        )


if __name__ == "__main__":
    unittest.main()

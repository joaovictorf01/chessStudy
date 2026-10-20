# This file is covered by the GNU General Public License.
# See the file COPYING.txt for more details.

"""What "Copy details" copies after a failed download: versions, what failed, and every cause."""

import unittest
import urllib.error

from chessStudy.error_details import error_details
from chessStudy.tactic.download import DownloadError

VERSIONS = {"addon_version": "2.1.0", "nvda_version": "2026.2.0", "windows_version": "10.0.26100"}


def raised_download_error() -> DownloadError:
	try:
		try:
			raise urllib.error.URLError("[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed")
		except urllib.error.URLError as error:
			raise DownloadError(f"download: KQvK.rtbw: {error}") from error
	except DownloadError as error:
		return error


class ErrorDetailsTest(unittest.TestCase):
	def test_versions_and_what_failed_come_first(self):
		text = error_details("tablebase download", DownloadError("HTTP 404"), **VERSIONS)
		self.assertEqual(
			text.splitlines(),
			[
				"Chess Study 2.1.0, NVDA 2026.2.0, Windows 10.0.26100",
				"Failed: tablebase download",
				"Error: DownloadError: HTTP 404",
			],
		)

	def test_the_cause_that_names_the_real_problem_is_kept(self):
		lines = error_details("tablebase download", raised_download_error(), **VERSIONS).splitlines()
		self.assertTrue(lines[2].startswith("Error: DownloadError: download: KQvK.rtbw:"))
		self.assertEqual(
			lines[3],
			"Caused by: URLError: <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed>",
		)
		self.assertEqual(len(lines), 4)

	def test_an_error_raised_while_handling_another_shows_both(self):
		try:
			try:
				raise OSError(28, "No space left on device")
			except OSError:
				raise RuntimeError("cleanup failed")
		except RuntimeError as error:
			lines = error_details("puzzle download", error, **VERSIONS).splitlines()
		self.assertEqual(lines[2], "Error: RuntimeError: cleanup failed")
		self.assertEqual(lines[3], "Caused by: OSError: [Errno 28] No space left on device")

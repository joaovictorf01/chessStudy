# coding: utf-8
# pyright: basic

# This file is covered by the GNU General Public License.
# See the file COPYING.txt for more details.

"""The text that "Copy details" puts on the clipboard after a failure.

Free of NVDA imports: the dialog passes the versions in. The text is for the
person who fixes the bug, so it stays in English whatever the interface
language, and it follows the chain of causes down to the one that names the
real problem (a certificate, a proxy, a full disk), which the message on
screen shortens.
"""

import typing as t


def error_details(
	what: str,
	error: BaseException,
	*,
	addon_version: str,
	nvda_version: str,
	windows_version: str,
) -> str:
	lines = [
		f"Chess Study {addon_version}, NVDA {nvda_version}, Windows {windows_version}",
		f"Failed: {what}",
	]
	for depth, link in enumerate(_causes(error)):
		label = "Error" if depth == 0 else "Caused by"
		lines.append(f"{label}: {type(link).__name__}: {link}")
	return "\n".join(lines)


def _causes(error: BaseException) -> t.Iterator[BaseException]:
	seen: set[int] = set()
	link: t.Optional[BaseException] = error
	while link is not None and id(link) not in seen:
		seen.add(id(link))
		yield link
		link = link.__cause__ or (None if link.__suppress_context__ else link.__context__)

"""Download the FIPS PDS products used by the James et al. (2020) workflow."""

from concurrent.futures import ThreadPoolExecutor, as_completed
from html.parser import HTMLParser
import os
from pathlib import Path
import time
from urllib.error import URLError
from urllib.parse import unquote, urljoin, urlparse, urlunparse
from urllib.request import Request, urlopen


PPI_DATA = "https://pds-ppi.igpp.ucla.edu/data/"
COLLECTIONS = (
	"mess-epps-fips-raw/data/scan/",
	"mess-epps-fips-calibrated/data/scan/",
	"mess-epps-fips-derived/data-fips-espec/",
	"mess-epps-fips-derived/data-fips-ntp/",
)
USER_AGENT = "PyMess-FIPS-downloader/1.0"


class _LinkParser(HTMLParser):
	def __init__(self):
		super().__init__()
		self.links = []

	def handle_starttag(self, tag, attrs):
		if tag.lower() == "a":
			for key, value in attrs:
				if key.lower() == "href" and value:
					self.links.append(value)


def _ReadIndex(url, Retries, Timeout):
	"""Return the child URLs in one PDS/PPI directory index."""
	last_error = None
	for attempt in range(Retries + 1):
		try:
			request = Request(url, headers={"User-Agent": USER_AGENT})
			with urlopen(request, timeout=Timeout) as response:
				parser = _LinkParser()
				parser.feed(response.read().decode("utf-8", "replace"))
				break
		except (URLError, TimeoutError, OSError) as error:
			last_error = error
			if attempt < Retries:
				time.sleep(min(2**attempt, 10))
	else:
		raise RuntimeError("Failed to read PDS index {:s}: {}".format(url, last_error))

	root = urlparse(PPI_DATA)
	current_path = urlparse(url).path
	if not current_path.endswith("/"):
		current_path += "/"
	children = []
	for link in parser.links:
		parsed = urlparse(urljoin(url, link))
		if parsed.netloc != root.netloc or not parsed.path.startswith(current_path):
			continue
		clean = urlunparse(parsed._replace(query="", fragment=""))
		if clean != url:
			children.append(clean)
	return sorted(set(children))


def _FindFiles(Retries, Timeout, Verbose=False):
	"""Recursively list files in the FIPS conversion collections."""
	stack = [urljoin(PPI_DATA, collection) for collection in COLLECTIONS]
	seen = set()
	files = []
	while stack:
		url = stack.pop()
		if url in seen:
			continue
		seen.add(url)
		for child in _ReadIndex(url, Retries, Timeout):
			if urlparse(child).path.endswith("/"):
				stack.append(child)
			else:
				files.append(child)
		if Verbose:
			print(
				"\rIndexed {:d} directories; found {:d} files".format(
					len(seen), len(files)
				),
				end="",
				flush=True,
			)
	if Verbose:
		print()
	return sorted(set(files))


def _DownloadFile(url, output, Overwrite, Retries, Timeout):
	path = unquote(urlparse(url).path)
	relative = path.split("/data/", 1)[1]
	destination = output / relative
	if destination.is_file() and not Overwrite:
		return "skipped", relative

	destination.parent.mkdir(parents=True, exist_ok=True)
	temporary = destination.with_name(destination.name + ".part")
	last_error = None
	for attempt in range(Retries + 1):
		try:
			request = Request(url, headers={"User-Agent": USER_AGENT})
			with urlopen(request, timeout=Timeout) as response, temporary.open("wb") as handle:
				while True:
					block = response.read(1024 * 1024)
					if not block:
						break
					handle.write(block)
			temporary.replace(destination)
			return "downloaded", relative
		except (URLError, TimeoutError, OSError) as error:
			last_error = error
			if attempt < Retries:
				time.sleep(min(2**attempt, 10))
	return "failed", "{:s}: {}".format(relative, last_error)


def DownloadData(Overwrite=False, Workers=4, Retries=3, Timeout=60, Output=None,
				 Verbose=True):
	"""Mirror the FIPS EDR scan, CDR scan, ESPEC and NTP collections.

	Files are placed below ``$MESSENGER_PATH/FIPS/PDS/pds_messenger_fips``
	with their PDS/PPI directory structure intact. Existing files are skipped
	unless ``Overwrite`` is true. ``Output`` may be supplied to use a different
	destination directory. Set ``Verbose=False`` to suppress progress output.

	Returns a dictionary containing ``downloaded``, ``skipped`` and ``failed``
	file counts. A failed download also raises ``RuntimeError`` after all work
	has completed.
	"""
	if Output is None:
		messenger_path = os.getenv("MESSENGER_PATH")
		if not messenger_path:
			raise RuntimeError("MESSENGER_PATH is not set")
		output = Path(messenger_path) / "FIPS" / "PDS" / "pds_messenger_fips"
	else:
		output = Path(Output).expanduser()

	if Verbose:
		print("Discovering MESSENGER FIPS PDS files...", flush=True)
	files = _FindFiles(Retries, Timeout, Verbose)
	if Verbose:
		print("Processing {:d} files using {:d} workers...".format(
			len(files), max(int(Workers), 1)
		), flush=True)
	counts = {"downloaded": 0, "skipped": 0, "failed": 0}
	failures = []
	with ThreadPoolExecutor(max_workers=max(int(Workers), 1)) as executor:
		jobs = [
			executor.submit(_DownloadFile, url, output, Overwrite, Retries, Timeout)
			for url in files
		]
		for completed, job in enumerate(as_completed(jobs), 1):
			status, message = job.result()
			counts[status] += 1
			if status == "failed":
				failures.append(message)
			if Verbose:
				print(
					"\rFiles {:d}/{:d}: downloaded={:d}, skipped={:d}, failed={:d}".format(
						completed, len(files), counts["downloaded"],
						counts["skipped"], counts["failed"]
					),
					end="",
					flush=True,
				)
	if Verbose:
		print()

	if failures:
		raise RuntimeError(
			"Failed to download {:d} FIPS PDS file(s):\n{}".format(
				len(failures), "\n".join(failures)
			)
		)
	if Verbose:
		print(
			"FIPS PDS download complete: downloaded={:d}, skipped={:d}, failed={:d}".format(
				counts["downloaded"], counts["skipped"], counts["failed"]
			),
			flush=True,
		)
	return counts

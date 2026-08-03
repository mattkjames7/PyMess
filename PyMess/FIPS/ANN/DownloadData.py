"""Download the ANN classification data published with James et al. (2020)."""

import hashlib
import json
from pathlib import Path
import time
from urllib.error import URLError
from urllib.request import Request, urlopen

from ... import Globals


ARTICLE_API = "https://api.figshare.com/v2/articles/11385897/versions/2"
DATA_NAME = "FIPSProtonClass.dat"
USER_AGENT = "PyMess-ANN-downloader/1.0"


def _Open(url, Retries, Timeout):
	last_error = None
	for attempt in range(Retries + 1):
		try:
			request = Request(url, headers={"User-Agent": USER_AGENT})
			return urlopen(request, timeout=Timeout)
		except (URLError, TimeoutError, OSError) as error:
			last_error = error
			if attempt < Retries:
				time.sleep(min(2**attempt, 10))
	raise RuntimeError("Failed to download {:s}: {}".format(url, last_error))


def _FileMetadata(Retries, Timeout):
	with _Open(ARTICLE_API, Retries, Timeout) as response:
		article = json.loads(response.read().decode("utf-8"))
	for item in article.get("files", []):
		if item.get("name") == DATA_NAME:
			return item
	raise RuntimeError("{:s} is not listed in the Figshare article".format(DATA_NAME))


def _MD5(filename):
	digest = hashlib.md5()
	with filename.open("rb") as handle:
		while True:
			block = handle.read(1024 * 1024)
			if not block:
				break
			digest.update(block)
	return digest.hexdigest()


def DownloadData(Overwrite=False, Verbose=True, Retries=3, Timeout=60):
	"""Download ``FIPSProtonClass.dat`` from the Figshare article.

	The file is written to ``$MESSENGER_PATH/FIPS/ANN``. The Figshare file
	size and MD5 checksum are verified before the temporary download is moved
	into place. Existing valid data are skipped unless ``Overwrite`` is true.

	Returns the path of the downloaded (or existing valid) data file.
	"""
	if not Globals.MessPath:
		raise RuntimeError("MESSENGER_PATH is not set")

	output = Path(Globals.MessPath) / "FIPS" / "ANN"
	output.mkdir(parents=True, exist_ok=True)
	destination = output / DATA_NAME
	temporary = destination.with_name(destination.name + ".part")

	if Verbose:
		print("Reading ANN data metadata from Figshare...", flush=True)
	metadata = _FileMetadata(Retries, Timeout)
	expected_size = int(metadata["size"])
	expected_md5 = metadata.get("computed_md5") or metadata.get("supplied_md5")

	if destination.is_file() and not Overwrite:
		if destination.stat().st_size == expected_size and (
				not expected_md5 or _MD5(destination) == expected_md5
		):
			if Verbose:
				print("ANN data already downloaded and verified: {:s}".format(
					str(destination)
				), flush=True)
			return str(destination)

	last_error = None
	for attempt in range(Retries + 1):
		try:
			downloaded = 0
			with _Open(metadata["download_url"], 0, Timeout) as response, \
					temporary.open("wb") as handle:
				while True:
					block = response.read(1024 * 1024)
					if not block:
						break
					handle.write(block)
					downloaded += len(block)
					if Verbose:
						percent = 100.0 * downloaded / expected_size
						print(
							"\rDownloading ANN data: {:5.1f}% ({:.1f}/{:.1f} MB)".format(
								min(percent, 100.0), downloaded / 1048576.0,
								expected_size / 1048576.0
							),
							end="",
							flush=True,
						)
			if Verbose:
				print()
			if temporary.stat().st_size != expected_size:
				raise RuntimeError(
					"Downloaded size is {:d} bytes; expected {:d}".format(
						temporary.stat().st_size, expected_size
					)
				)
			if expected_md5 and _MD5(temporary) != expected_md5:
				raise RuntimeError("Downloaded ANN data failed its MD5 check")
			temporary.replace(destination)
			if Verbose:
				print("ANN data downloaded and verified: {:s}".format(
					str(destination)
				), flush=True)
			return str(destination)
		except (URLError, TimeoutError, OSError, RuntimeError) as error:
			last_error = error
			if attempt < Retries:
				time.sleep(min(2**attempt, 10))

	raise RuntimeError("Failed to download ANN data: {}".format(last_error))

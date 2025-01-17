import asyncio
import itertools
import re
import aiohttp
import requests
from typing import Dict, List, Callable

from gistapi import util

# bigger files are not searched now
MAX_FILE_SIZE = 5


def get_gists_for_user(username: str):
    """Provides the list of gist metadata for a given user.
    This abstracts the /users/:username/gist endpoint from the Github API.
    See https://developer.github.com/v3/gists/#list-a-users-gists for
    more information.
    Args:
        username (string): the user to query gists for
    Returns:
        The list of dicts parsed from the json response from the Github API.  See
        the above URL for details of the expected structure.
    """
    per_page = 100
    gists_for_user = []
    found_page_with_less_than_maximum_items = False
    page = 1

    while not found_page_with_less_than_maximum_items:
        gists_url = f'https://api.github.com/users/{username}/gists?per_page={per_page}&page={page}'
        try:
            response = requests.get(gists_url)
            if response.status_code != 200:
                raise ValueError('Invalid GitHub API call, most probably not existing username')
        except requests.exceptions.ConnectionError as ex:
            raise requests.exceptions.ConnectionError('Github api is not available currently')

        gists_on_current_page = response.json()
        gists_for_user.extend(gists_on_current_page)
        found_page_with_less_than_maximum_items = len(gists_on_current_page) < per_page
        page += 1

    return gists_for_user


def get_raw_file_urls_by_gists(gists) -> Dict[str, List[str]]:
    """Takes the valuable data from gists of user which is in the form
    that the github api returned
        Args:
            gists
        Returns:
            The dict with valuable data in the following form:
            {<gist_url>: [<raw_file_urls>]}.
        """
    raw_file_urls_by_gists = {}
    for gist in gists:
        gist_url = gist['html_url']
        raw_file_urls_by_gists[gist_url] = []
        for file_properties in gist.get('files', {}).values():
            file_url = file_properties.get('raw_url', None)
            if file_url:
                raw_file_urls_by_gists[gist_url].append(file_url)
    return raw_file_urls_by_gists


def get_file_size_by_url(file_url: str):
    # https://stackoverflow.com/a/55226651
    response = requests.head(file_url, allow_redirects=True)
    size_in_bites = response.headers.get('content-length', -1)
    size_in_mb = int(size_in_bites) / float(1 << 20)
    return size_in_mb

async def download_file_and_map(file_url, session: aiohttp.ClientSession, map_function: Callable):
    file_size = get_file_size_by_url(file_url)
    if MAX_FILE_SIZE < file_size:
        return False

    async with session.get(url=file_url) as response:
        resp = await response.text()
        return map_function(resp) if map_function else resp


async def check_files_from_net_against_pattern(file_urls: List[str], pattern: str) -> Dict[str, bool]:
    """
    Downloads all given files and check them against pattern
        Args:
            file_urls: url for the files to download
            pattern: regexp pattern
        Returns:
            The dict where file urls are the keys and the value is True if the file matches
            the given pattern.
    """
    compiled_pattern = re.compile(pattern)
    # intentionally defined with lambda (instead of in a normal function) to avoid passing the pattern over again
    pattern_checker = lambda text: re.search(compiled_pattern, text)
    async with aiohttp.ClientSession() as session:
        # "gather" function runs download_file_and_map function calls in parallel and collects
        # their returned value in a list in the same order as the function calls were
        matching_data_of_files = await asyncio.gather(
            *[download_file_and_map(file_url, session, pattern_checker) for file_url in file_urls]
        )
        return dict(zip(file_urls, matching_data_of_files))


@util.timeit
def get_matching_gist_urls_async(username: str, pattern: str) -> List[str]:
    """
    Async solution which uses aiohttp and asyncio to download and check files in parallel

    Returns:
        The dict with valuable data in the following form:
        {<gist_url>: [<raw_file_urls>]}.
    """
    gists = get_gists_for_user(username)
    raw_file_urls_by_gists = get_raw_file_urls_by_gists(gists)
    all_raw_file_urls: List[str] = list(itertools.chain.from_iterable(raw_file_urls_by_gists.values()))
    matching_data_of_files: Dict[str, bool] = asyncio.run(check_files_from_net_against_pattern(all_raw_file_urls, pattern))
    matching_gist_urls = []

    for gist_url, raw_file_urls_by_gists in raw_file_urls_by_gists.items():
        for raw_file_url in raw_file_urls_by_gists:
            if matching_data_of_files.get(raw_file_url, False):
                matching_gist_urls.append(gist_url)
                break

    return matching_gist_urls


@util.timeit
def get_matching_gist_urls_sync(username: str, pattern: str) -> List[str]:
    """
    Sync solution which simply gets all the files of all gists sequentially and
    check them against the regexp pattern.

    Returns:
        The dict with valuable data in the following form:
        {<gist_url>: [<raw_file_urls>]}.
    """
    gists = get_gists_for_user(username)
    raw_file_urls_by_gists = get_raw_file_urls_by_gists(gists)
    file_contents = {}
    for gist_url, raw_file_urls_by_gists in raw_file_urls_by_gists.items():
        file_contents[gist_url] = []
        for raw_file_url in raw_file_urls_by_gists:
            file_size = get_file_size_by_url(raw_file_url)
            if MAX_FILE_SIZE < file_size:
                continue

            response = requests.get(raw_file_url)
            file_contents[gist_url].append(response.text)

    matching_gist_urls = []
    compiled_pattern = re.compile(pattern)
    for gist_url, file_contents in file_contents.items():
        for file_content in file_contents:
            if re.search(compiled_pattern, file_content):
                matching_gist_urls.append(gist_url)
                break

    return matching_gist_urls

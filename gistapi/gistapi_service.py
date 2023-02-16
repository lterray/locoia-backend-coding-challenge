import asyncio
import itertools
import re
import aiohttp
import requests
from typing import Dict, List, Callable

from util import timeit


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
        except requests.exceptions.ConnectionError as ex:
            raise requests.exceptions.ConnectionError('Github api is not available currently')

        gists_on_current_page = requests.get(gists_url).json()
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


async def download_file_and_map(file_url, session: aiohttp.ClientSession, map_function: Callable):
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


@timeit
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


@timeit
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

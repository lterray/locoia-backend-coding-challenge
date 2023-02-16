from gistapi import gistapi_service
from .utils_for_tests import fake_user_gists


def test_get_raw_file_urls_by_gists_normal(fake_user_gists):
    raw_file_urls_by_gists = gistapi_service.get_raw_file_urls_by_gists(fake_user_gists)
    desired_result = {
        'gist_with_pattern': ['gists.com/file_with_pattern_1.txt',
                              'gists.com/file_without_pattern_1.txt'],
        'gist_without_pattern': ['gists.com/file_without_pattern_1.txt',
                                 'gists.com/file_without_pattern_2.txt']
    }
    assert raw_file_urls_by_gists == desired_result


def test_get_raw_file_urls_by_gists_normal(fake_user_gists):
    raw_file_urls_by_gists = gistapi_service.get_raw_file_urls_by_gists(fake_user_gists)
    desired_result = {
        'gist_with_pattern': ['gists.com/file_with_pattern_1.txt',
                              'gists.com/file_without_pattern_1.txt'],
        'gist_without_pattern': ['gists.com/file_without_pattern_1.txt',
                                 'gists.com/file_without_pattern_2.txt']
    }
    assert raw_file_urls_by_gists == desired_result
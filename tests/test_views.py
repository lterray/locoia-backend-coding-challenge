import logging
from .utils_for_tests import client, fake_user_gists

LOGGER = logging.getLogger(__name__)


def test_without_mock(client, fake_user_gists, mocker):
    # we don't test the sync version
    mocker.patch("gistapi.gistapi_service.get_matching_gist_urls_sync", return_value=[])
    response = client.get('/api/v1/search?username=justdionysus&pattern=import%20requests')
    assert response.status_code == 200
    response_object = response.json
    # LOGGER.info(response_object)
    assert response_object.get('matches_async') == ['https://gist.github.com/65e6162d99c2e2ea8049b0584dd00912']


def test_with_mock(client, fake_user_gists, mocker):
    # we don't test the sync version
    mocker.patch("gistapi.gistapi_service.get_matching_gist_urls_sync", return_value=[])
    # mock github api to return user gists from fixture 'fake_user_gists'
    mocker.patch("gistapi.gistapi_service.get_gists_for_user", return_value=fake_user_gists)

    # mock function to find pattern if the file name contains 'with_pattern'
    def mock_download_file_and_map(file_url, *args, **kwargs):
        return 'with_pattern' in file_url
    mocker.patch("gistapi.gistapi_service.download_file_and_map", wraps=mock_download_file_and_map)

    response = client.get('/api/v1/search?username=mock_user&pattern=mock_pattern')
    assert response.status_code == 200
    response_object = response.json
    # LOGGER.info(response_object)
    assert response_object.get('matches_async') == ['gist_with_pattern']
import pytest
import main


@pytest.fixture
def client():
    main.app.testing = True
    return main.app.test_client()


@pytest.fixture
def fake_user_gists():
    return [
        {
            'html_url': 'gist_with_pattern',
            'files': {
                'file_1': {
                    'raw_url': 'gists.com/file_with_pattern_1.txt'
                },
                'file_2': {
                    'raw_url': 'gists.com/file_without_pattern_1.txt'
                }
            }
        },
        {
            'html_url': 'gist_without_pattern',
            'files': {
                'file_1': {
                    'raw_url': 'gists.com/file_without_pattern_1.txt'
                },
                'file_2': {
                    'raw_url': 'gists.com/file_without_pattern_2.txt'
                }
            }
        }
    ]
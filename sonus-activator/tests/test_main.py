import os
from ..main import get_project_id


def test_get_project_id():
    # Test with environment variable set
    os.environ['PROJECT_ID'] = 'test-project'
    assert get_project_id() == 'test-project'

    # Test with environment variable unset
    os.environ.pop('PROJECT_ID', None)
    assert get_project_id() == ''

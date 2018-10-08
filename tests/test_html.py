from .fixtures import app_client

def test_homepage(app_client):
    response = app_client.get('/', gather_request=False)
    assert response.status == 200
    assert 'dummy_tables' in response.text

def test_database_page(app_client):
    response = app_client.get('/dummy_tables', allow_redirects=False, gather_request=False)
    assert response.status == 302
    response = app_client.get('/dummy_tables', gather_request=False)
    assert 'dummy_tables' in response.text

def test_table(app_client):
    response = app_client.get('/dummy_tables/table2', gather_request=False)
    assert response.status == 200

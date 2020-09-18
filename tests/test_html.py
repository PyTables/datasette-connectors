from .fixtures import app_client, app_client_with_hash

def test_homepage(app_client):
    response = app_client.get('/')
    assert response.status == 200
    assert 'dummy_tables' in response.text

def test_database_page(app_client_with_hash):
    response = app_client_with_hash.get('/dummy_tables', allow_redirects=False)
    assert response.status == 302
    response = app_client_with_hash.get('/dummy_tables')
    assert 'dummy_tables' in response.text

def test_table(app_client):
    response = app_client.get('/dummy_tables/table2')
    assert response.status == 200

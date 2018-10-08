from .fixtures import app_client
from urllib.parse import urlencode

def test_homepage(app_client):
    _, response = app_client.get('/.json')
    assert response.status == 200
    assert response.json.keys() == {'dummy_tables': 0}.keys()
    d = response.json['dummy_tables']
    assert d['name'] == 'dummy_tables'
    assert d['tables_count'] == 2

def test_database_page(app_client):
    response = app_client.get('/dummy_tables.json', gather_request=False)
    data = response.json
    assert 'dummy_tables' == data['database']
    assert [{
        'name': 'table1',
        'columns': ['c1', 'c2', 'c3'],
        'primary_keys': [],
        'count': 2,
        'label_column': None,
        'hidden': False,
        'fts_table': None,
        'foreign_keys': {'incoming': [], 'outgoing': []}
    }, {
        'name': 'table2',
        'columns': ['c1', 'c2', 'c3'],
        'primary_keys': [],
        'count': 2,
        'label_column': None,
        'hidden': False,
        'fts_table': None,
        'foreign_keys': {'incoming': [], 'outgoing': []}
    }] == data['tables']

def test_custom_sql(app_client):
    response = app_client.get(
        '/dummy_tables.json?' + urlencode({
            'sql': 'select c1 from table1',
            '_shape': 'objects'
        }),
        gather_request=False
    )
    data = response.json
    assert {
        'sql': 'select c1 from table1',
        'params': {}
    } == data['query']
    assert 2 == len(data['rows'])
    assert [
        {'c1': 10},
        {'c1': 20}
    ] == data['rows']
    assert ['c1'] == data['columns']
    assert 'dummy_tables' == data['database']
    assert not data['truncated']

def test_invalid_custom_sql(app_client):
    response = app_client.get(
        '/dummy_tables.json?sql=.schema',
        gather_request=False
    )
    assert response.status == 400
    assert response.json['ok'] is False
    assert 'Statement must be a SELECT' == response.json['error']

def test_table_json(app_client):
    response = app_client.get(
        '/dummy_tables/table2.json?_shape=objects',
        gather_request=False
    )
    assert response.status == 200
    data = response.json
    assert data['query']['sql'] == 'select rowid, * from table2 order by rowid limit 51'
    assert data['rows'] == [{
        'rowid': 1,
        'c1': 100,
        'c2': 120,
        'c3': 130
    }, {
        'rowid': 2,
        'c1': 200,
        'c2': 220,
        'c3': 230
    }]

def test_table_not_exists_json(app_client):
    assert {
        'ok': False,
        'error': 'Table not found: blah',
        'status': 404,
        'title': None,
    } == app_client.get(
        '/dummy_tables/blah.json', gather_request=False
    ).json

def test_table_shape_arrays(app_client):
    response = app_client.get(
        '/dummy_tables/table2.json?_shape=arrays',
        gather_request=False
    )
    assert [
        [1, 100, 120, 130],
        [2, 200, 220, 230],
    ] == response.json['rows']

def test_table_shape_objects(app_client):
    response = app_client.get(
        '/dummy_tables/table2.json?_shape=objects',
        gather_request=False
    )
    assert [{
        'rowid': 1,
        'c1': 100,
        'c2': 120,
        'c3': 130,
    }, {
        'rowid': 2,
        'c1': 200,
        'c2': 220,
        'c3': 230,
    }] == response.json['rows']

def test_table_shape_array(app_client):
    response = app_client.get(
        '/dummy_tables/table2.json?_shape=array',
        gather_request=False
    )
    assert [{
        'rowid': 1,
        'c1': 100,
        'c2': 120,
        'c3': 130,
    }, {
        'rowid': 2,
        'c1': 200,
        'c2': 220,
        'c3': 230,
    }] == response.json

def test_table_shape_invalid(app_client):
    response = app_client.get(
        '/dummy_tables/table2.json?_shape=invalid',
        gather_request=False
    )
    assert {
        'ok': False,
        'error': 'Invalid _shape: invalid',
        'status': 400,
        'title': None,
    } == response.json

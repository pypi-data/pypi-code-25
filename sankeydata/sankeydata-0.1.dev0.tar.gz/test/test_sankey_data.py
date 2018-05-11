import pytest
import json
import jsonschema
import os.path

from sankeydata import SankeyData, SankeyNode, SankeyLink

SCHEMA_FILENAME = os.path.join(os.path.dirname(__file__),
                               '../src/json-sankey-schema.json')

def test_sankey_data():
    nodes = {}
    links = {}
    groups = {}
    data = SankeyData(nodes, links, groups)
    assert data.nodes is nodes
    assert data.links is links
    assert data.groups is groups


def test_sankey_data_json():
    data = SankeyData(nodes=[SankeyNode(id='a')],
                      links=[SankeyLink(source='a', target='a')])
    data_json = data.to_json()
    assert data_json['nodes'] == [n.to_json() for n in data.nodes]
    assert data_json['links'] == [l.to_json() for l in data.links]


def test_sankey_data_json_validates():
    data = SankeyData(nodes=[SankeyNode(id='a')],
                      links=[SankeyLink(source='a', target='a')])
    data_json = data.to_json()

    with open(SCHEMA_FILENAME, 'rt') as f:
        schema = json.load(f)

    jsonschema.validate(data_json, schema)


def test_sankey_data_node_json():
    assert SankeyNode(id='a').to_json() == {
        'id': 'a',
        'title': {
            'label': 'a',
        },
        'style': {
            'direction': 'r',
            'hidden': False,
            'type': 'default',
        }
    }

    assert SankeyNode(id='a', title='A').to_json()['title']['label'] == 'A', \
        'title can be overridden'

    assert SankeyNode(id='a', direction='L').to_json()['style']['direction'] == 'l', \
        'direction can be set'

    assert SankeyNode(id='a', title='').to_json()['style']['hidden'] == True, \
        'hidden when title == ""'

    assert SankeyNode(id='a', hidden=True).to_json()['style']['hidden'] == True, \
        'hidden when hidden == True'


def test_sankey_data_link_required_attrs():
    with pytest.raises(TypeError):
        SankeyLink(source='a')
    with pytest.raises(TypeError):
        SankeyLink(target='a')


def test_sankey_data_link_default_values():
    assert SankeyLink('a', 'b').type == None


def test_sankey_data_link_json():
    link = SankeyLink('a', 'b', type='c', time='d', value=2, title='link',
                      opacity=0.9, color='blue')

    # draft JSON Sankey serialisation format
    assert link.to_json() == {
        'source': 'a',
        'target': 'b',
        'type': 'c',
        # 'time': 'd',
        'data': {
            'value': 2,
        },
        # 'title': 'link',
        'style': {
            'opacity': 0.9,
            'color': 'blue',
        }
    }

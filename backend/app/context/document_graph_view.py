"""Read the prebuilt corpus graph for the shared demo."""
from collections import defaultdict
from functools import cached_property
import json
import unicodedata


def search_key(text):
    normalized = unicodedata.normalize('NFD', text.casefold().replace('đ', 'd'))
    return ''.join(char for char in normalized if not unicodedata.combining(char))


class DocumentGraphView:
    def __init__(self, path):
        graph = json.loads(path.read_text(encoding='utf-8'))
        self.nodes = {node['id']: node for node in graph['nodes']}
        self.edges = graph['edges']
        self.incident = defaultdict(list)
        for edge in self.edges:
            for key in ('source_id', 'target_id'):
                node_id = edge[key]
                if node_id not in self.nodes:
                    raise ValueError('Graph edge has an unknown endpoint')
                self.incident[node_id].append(edge)
        self.summary = dict(node_count=len(self.nodes), edge_count=len(graph['edges']))
        self.default_id = ('dataset:56666' if 'dataset:56666' in self.nodes
                           else next(iter(self.incident), next(iter(self.nodes), None)))
        self.index = [
            (search_key(' '.join(node.get(field) or '' for field in
                                 ('number', 'number_raw', 'title', 'id'))), node)
            for node in self.nodes.values()
        ]

    @cached_property
    def overview(self):
        """Return the whole topology. Evidence is fetched in the selected view."""
        indices = {key: index for index, key in enumerate(self.nodes)}
        return {
            **self.summary,
            'nodes': [
                dict(id=node['id'], number=node.get('number') or node.get('number_raw'),
                     title=node.get('title'), full_text_status=node['full_text_status'])
                for node in self.nodes.values()
            ],
            'edges': [
                [indices[edge['source_id']], indices[edge['target_id']], edge['relation']]
                for edge in self.edges
            ],
        }

    def selection(self, node_id, offset, limit):
        node = self.nodes[node_id]
        edges = self.incident.get(node_id, [])
        page = edges[offset:offset + limit]
        neighbor_ids = dict.fromkeys(edge['target_id'] if edge['source_id'] == node_id
                                     else edge['source_id'] for edge in page)
        return dict(node=node, neighbors=[self.nodes[key] for key in neighbor_ids],
                    edges=page, total=len(edges), offset=offset, limit=limit)

    def search(self, query, offset, limit):
        terms = search_key(query).split()
        matches = [node for key, node in self.index if all(term in key for term in terms)]
        return dict(matches=matches[offset:offset + limit], total=len(matches),
                    offset=offset, limit=limit)

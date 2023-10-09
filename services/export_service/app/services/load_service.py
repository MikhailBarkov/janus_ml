from itertools import chain

from gremlin_python.process.graph_traversal import __
from gremlin_python.process.traversal import T

from db import get_gremlin_connection
from models import (
    RequestBody,
    PGTarget,
    PGFeature,
)
from settings import config


class LoadService:

    @classmethod
    async def create(cls, endpoint):
        self = LoadService()
        self.g = await get_gremlin_connection(endpoint)
        return self

    async def load(self, get_traversal):
        n = await get_traversal().count().next()

        objects = []
        batch_size = config.gremlin_batch_size

        traversal = get_traversal()
        for i in range(n//batch_size):
            objects.extend(await traversal.next(batch_size))

        objects.extend(await traversal.next(n%batch_size))

        return objects

    async def load_nodes(self, label: str, properties: list[str]):

        def get_traversal(label=label, properties=properties):
            if not properties[0]:
                properties = []

            if 'label' in properties:
                idx = properties.index('label')
                properties[idx] = T.label

            all_properties = ['node_id'] + properties

            traversal = (
                self.g.V()
                .hasLabel(label)
                .project(*all_properties)
                .by(T.id)
            )

            for property in properties:
                traversal = traversal.by(property)

            return traversal

        return await self.load(get_traversal)

    async def load_edges(self, edge: tuple[str, str, str], properties: list[str]):

        def get_traversal(edge=edge, properties=properties):
            if not properties[0]:
                properties = []

            if 'label' in properties:
                idx = properties.index('label')
                properties[idx] = T.label

            all_properties = ['src_id', 'dst_id'] + properties

            traversal = (
                self.g.E()
                .hasLabel(edge.label)
                .and_(
                    __.outV().hasLabel(edge.out),
                    __.inV().hasLabel(edge.in_)
                )
                .project(*all_properties)
                .by(__.outV().id())
                .by(__.inV().id())
            )

            for property in properties:
                traversal = traversal.by(property)

            return traversal

        return await self.load(get_traversal)

    async def inductive_load(
        self, node_id, node_params, edge, edge_properties, n_layers
    ):
        def get_traversal(
            node_id=node_id,
            node_params=node_params,
            edge=edge,
            edge_properties=edge_properties,
            n_layers=n_layers
        ):
            #TODO: change for heterogenus graph
            node_properties = node_params[edge.out]

            if 'label' in node_properties:
                idx = node_properties.index('label')
                node_properties[idx] = T.label

            all_properties = ['node_id'] + node_properties + ['edges']

            traversal = (
                self.g
                .V(node_id)
                .emit()
                .repeat(__.hasLabel(edge.out).both(edge.label).hasLabel(edge.in_))
                .times(n_layers)
                .project(*all_properties)
                .by(T.id)
            )

            for property in node_properties:
                traversal = traversal.by(property)

            edge_properties = ['label']

            all_edge_properties = ['edge_id', 'src_id', 'dst_id'] + edge_properties

            if 'label' in edge_properties:
                idx = edge_properties.index('label')
                edge_properties[idx] = T.label

            edge_trav = (
                __.outE(edge.label)
                .project(*all_edge_properties)
                .by(__.id())
                .by(__.outV().id())
                .by(__.inV().id())
            )

            for property in edge_properties:
                edge_trav = edge_trav.by(property)

            traversal = traversal.by(edge_trav.fold())

            return traversal

        response = await self.load(get_traversal)

        return self.extract(response, node_params[edge.out], edge_properties)

    def extract(self, response, node_properties, edge_properties):
        nodes, edges = [], []

        nodes_id = set()
        for node in response:
            if not node['node_id'] in nodes_id:
                nodes_id.add(node['node_id'])
                nodes.append(node)

        for node in nodes:
            for edge in node['edges']:
                if edge['dst_id'] in nodes_id:
                    edges.append(edge)

        return nodes, edges

from itertools import chain
from typing import Callable

from gremlin_python.process.graph_traversal import __
from gremlin_python.process.traversal import T
from gremlin_python.process.traversal import P

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
        g = await get_gremlin_connection(endpoint)
        return cls(g)

    def __init__(self, g):
        self.g = g

    async def load_nodes(self, label: str, properties: list[str], traversal):

        def get_traversal(label=label, properties=properties, traversal=traversal):
            if not properties[0]:
                properties = []

            if 'label' in properties:
                idx = properties.index('label')
                properties[idx] = T.label

            all_properties = ['node_id'] + properties

            proj_traversal = (
                traversal
                .project(*all_properties)
                .by(T.id)
            )

            for property in properties:
                proj_traversal = proj_traversal.by(property)

            return proj_traversal

        return await get_traversal().toList()

    async def load_edges(self, edge: tuple[str, str, str], properties: list[str], traversal):

        def get_traversal(edge=edge, properties=properties, traversal=traversal):
            if not properties[0]:
                properties = []

            if 'label' in properties:
                idx = properties.index('label')
                properties[idx] = T.label

            all_properties = ['src_id', 'dst_id'] + properties

            proj_traversal = (
                traversal
                .project(*all_properties)
                .by(__.outV().id_())
                .by(__.inV().id_())
            )

            for property in properties:
                proj_traversal = proj_traversal.by(property)

            return proj_traversal

        return await get_traversal().toList()

    async def transductive_load_nodes(self, label: str, properties: list[str]):
        traversal = self.g.V().hasLabel(label)
        return await self.load_nodes(label, properties, traversal)

    async def transductive_load_edges(self, edge: tuple[str, str, str], properties: list[str]):
        traversal = (
            self.g
            .E()
            .hasLabel(edge.label)
            .and_(
                __.outV().hasLabel(edge.out),
                __.inV().hasLabel(edge.in_)
            )
        )
        return await self.load_edges(edge, properties, traversal)

    async def inductive_load(
        self,
        edge_label, edge_properties,
        node_label, node_properties,
        entity_id, n_layers, n_neighbors=25
    ):
        traversal = (
            self.g
            .V(entity_id)
            .hasLabel(edge_label.out)
            .local(
                __.inE(edge_label.label)
                .limit(n_neighbors)
            )
            .store('subgraph')
        )

        for _ in range(n_layers-1):
            traversal = traversal.local(
                __.outV()
                .hasLabel(edge_label.in_)
                .inE(edge_label.label)
                .limit(n_neighbors)
            ).store('subgraph')

        traversal = traversal.cap('subgraph').unfold()

        edges = await self.load_edges(edge_label, edge_properties, traversal)

        nodes_idxs = {edge['src_id'] for edge in edges}.union(
            {edge['dst_id'] for edge in edges}
        )

        traversal = self.g.V(nodes_idxs)
        nodes = await self.load_nodes(node_label, node_properties, traversal)

        return nodes, edges
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
                .hasLabel(label)
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
                .hasLabel(edge.label)
                .and_(
                    __.outV().hasLabel(edge.out),
                    __.inV().hasLabel(edge.in_)
                )
                .project(*all_properties)
                .by(__.outV().id_())
                .by(__.inV().id_())
            )

            for property in properties:
                proj_traversal = proj_traversal.by(property)

            return proj_traversal

        return await get_traversal().toList()

    async def transductive_load_nodes(self, label: str, properties: list[str]):
        traversal = self.g.V()
        return await self.load_nodes(label, properties, traversal)

    async def transductive_load_edges(self, edge: tuple[str, str, str], properties: list[str]):
        traversal = self.g.E()
        return await self.load_edges(edge, properties, traversal)

    async def inductive_load_nodes(
        self, label: str, properties: list[str], n_layers: int, node_id: int
    ):
        trav = self.g.V(node_id)
        for _ in range(n_layers):
            subgraph_trav = trav.in_()

        traversal = trav.dedup()

        return await self.load_nodes(label, properties, traversal)

    async def inductive_load_edges(
        self, edge: tuple[str, str, str], properties: list[str], n_layers:int, node_id: int
    ):
        subgraph_trav = self.g.V(node_id).hasLabel(edge[0])
        for _ in range(n_layers):
            subgraph_trav = subgraph_trav.in_(edge[1]).barrier()

        subgraph = await subgraph_trav.dedup().hasLabel(edge[2]).toList()

        traversal = (
            self.g.E()
            .hasLabel(edge[1])
            .where(
                __.and_(
                    __.outV().is_(P.within(subgraph)),
                    __.inV().is_(P.within(subgraph))
                )
            )
        )

        return await self.load_edges(edge, properties, traversal)

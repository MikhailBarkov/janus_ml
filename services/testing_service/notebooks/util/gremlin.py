import csv
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.driver.aiohttp.transport import AiohttpTransport
from gremlin_python.process.graph_traversal import __
from gremlin_python.process.traversal import P
from gremlin_python.process.traversal import T
from gremlin_python.statics import long, ListType


def upload_texas(janus_url="ws://janusgraph:8182/gremlin"):
    g = traversal().with_remote(DriverRemoteConnection(
        janus_url,'g',
        transport_factory=lambda:AiohttpTransport(call_from_event_loop=True))
    )

    print('Загрузка началась')

    nodes = []
    with open('util/data/texas_nodes.csv', 'r') as rf:
        reader = csv.DictReader(rf)
        for row in reader:
            nodes.append(
                g.addV('page')
                .property('category', row['category'])
                .property('word_vector', ListType([float(x) for x in row['word_vector'].lstrip('[').rstrip(']').split(', ')]))
                .next()
            )

    print('Вершины загружены')

    with open('util/data/texas_edges.csv', 'r') as rf:
        reader = csv.DictReader(rf)
        for row in reader:
            (
                g.addE('hyperlink')
                .from_(nodes[int(row['src_id'])])
                .to(nodes[int(row['dst_id'])])
                .iterate()
            )

    print('Загрузка завершена')


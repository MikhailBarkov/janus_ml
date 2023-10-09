import asyncio

from aiogremlin import DriverRemoteConnection, Graph

from settings import config


async def get_gremlin_connection(janus_url):
    remote_connection = await DriverRemoteConnection.open(janus_url, 'g')
    return Graph().traversal().withRemote(remote_connection)

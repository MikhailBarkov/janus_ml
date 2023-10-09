from aiohttp import web

from services import ProcService
from models import ProcParams


async def index(request):
    text = str(await request.read())
    return web.Response(text=text)


async def processing(request):
    request_body = await request.read()
    proc_params = ProcParams.parse_raw(request_body)

    service = ProcService(proc_params)
    data = await service.proc()

    return web.json_response(data)

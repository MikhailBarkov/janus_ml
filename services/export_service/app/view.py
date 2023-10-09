import json

from aiohttp import web

from models import RequestBody
from services import ExportService


async def index(request):
    text = str(await request.read())
    return web.Response(text=text)


async def export(request):
    request_body = await request.read()
    export_params = RequestBody.parse_raw(request_body)

    service = await ExportService.create(export_params)
    data = await service.export()

    return web.json_response(data)
    # return web.Response(
    #     status=200,
    #     content_type='application/json',
    #     text=json.dumps(data[0])
    # )
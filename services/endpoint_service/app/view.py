from aiohttp import web

from models import CreateRequest, CallRequest
from services import EndpointService


async def index(request):
    text = str(await request.read())

    return web.Response(text=text)


async def create_endpoint(request):
    request_body = await request.read()
    endpoint_params = CreateRequest.parse_raw(request_body)

    service = await EndpointService.create()
    await service.create_endpoint(endpoint_params)

    return web.Response(status=200, content_type='application/json', text='')


async def call_endpoint(request):
    request_body = await request.read()
    call_params = CallRequest.parse_raw(request_body)

    service = await EndpointService.create()
    prediction = await service.call(call_params)

    return web.Response(status=200, content_type='application/json', text=str(prediction))

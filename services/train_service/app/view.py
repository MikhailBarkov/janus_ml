from aiohttp import web

from models import TrainParams
from services import TrainService


async def index(request):
    text = str(await request.read())
    return web.Response(text=text)


async def modeltraining(request):
    request_body = await request.read()
    train_params = TrainParams.parse_raw(request_body)

    service = TrainService(train_params)
    response = await service.train()

    return web.json_response(response)

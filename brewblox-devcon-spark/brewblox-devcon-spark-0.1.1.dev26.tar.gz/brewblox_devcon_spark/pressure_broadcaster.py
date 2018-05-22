"""
Intermittently broadcasts pressure sensor state to the eventbus
"""


import asyncio
from concurrent.futures import CancelledError
from contextlib import suppress

from aiohttp import web
from brewblox_devcon_spark import pressure
from brewblox_service import brewblox_logger, events, features

LOGGER = brewblox_logger(__name__)
routes = web.RouteTableDef()


def get_broadcaster(app: web.Application):
    return features.get(app, PressureBroadcaster)


def setup(app: web.Application):
    app.router.add_routes(routes)
    features.add(app, PressureBroadcaster(app))


class PressureBroadcaster(features.ServiceFeature):

    def __init__(self, app: web.Application=None):
        super().__init__(app)
        self._task: asyncio.Task = None

    def __str__(self):
        return f'{type(self).__name__}'

    async def start(self, app: web.Application):
        await self.close()
        self._task = app.loop.create_task(self._broadcast(app))

    async def close(self, *_):
        with suppress(AttributeError, CancelledError):
            self._task.cancel()
            await self._task
        self._task = None

    async def recalculate(self, app: web.Application, input_file: str, name: str):
        publisher = events.get_publisher(app)
        sensor = pressure.get_sensor(app)
        exchange = app['config']['broadcast_exchange']
        num_published = 0

        async for val in sensor.recalculate(input_file):
            await publisher.publish(
                exchange=exchange,
                routing=name,
                message=val
            )
            num_published += 1

        return {'published': num_published}

    async def _broadcast(self, app: web.Application):
        sensor = pressure.get_sensor(app)
        publisher = events.get_publisher(app)
        name = app['config']['name']
        interval = app['config']['broadcast_interval']
        exchange = app['config']['broadcast_exchange']
        last_broadcast_ok = True

        LOGGER.info(f'{self} now broadcasting')

        while True:
            try:
                await asyncio.sleep(interval)
                state = sensor.latest

                # Don't broadcast when empty
                if not state:
                    continue

                await publisher.publish(
                    exchange=exchange,
                    routing=name,
                    message=state
                )

                if not last_broadcast_ok:
                    LOGGER.info(f'{self} resumed Ok')
                    last_broadcast_ok = True

            except CancelledError:
                break

            except Exception as ex:
                if last_broadcast_ok:
                    LOGGER.warn(f'{self} interrupted with error: {type(ex).__name__}={ex}')
                    last_broadcast_ok = False


@routes.post('/pressure/recalculate')
async def recalculate(request: web.Request) -> web.Response:
    """
    ---
    tags:
    - Pressure
    summary: recalculate csv file
    operationId: pressure.recalculate
    produces:
    - application/json
    parameters:
    -
        in: body
        name: body
        description: Query
        required: true
        schema:
            type: object
            properties:
                input_file:
                    type: string
                name:
                    type: string
    """
    args = await request.json()
    return await get_broadcaster(request.app).recalculate(
        app=request.app,
        input_file=args['input_file'],
        name=args['name']
    )

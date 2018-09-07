from signal import signal, SIGINT
from sanic import Sanic
from sanic.response import json
import aioredis
from settings import SETTINGS
from handlers.ws_room import WsRoom
from processors.receiver_processor import ReceiverProcessor
app = Sanic(__name__)
app.ws_list = {}


@app.listener('before_server_start')
async def setup_db(app, loop):
    """
    Инициализируем пулл коннектов к сервису сообщений
    по одному на подписку и публикацию.
    """
    app.messaging_pool_subscription = await aioredis.create_redis_pool(
        SETTINGS['REDIS']['CONN'],
        db=SETTINGS['REDIS']['DB'], loop=loop
    )
    app.messaging_pool_publish = await aioredis.create_redis_pool(
        SETTINGS['REDIS']['CONN'], db=SETTINGS['REDIS']['DB'],
        loop=loop
    )
    app.receiver = ReceiverProcessor(app=app)


@app.listener('after_server_stop')
async def close_db(app, loop):
    """
    При закрытии приложения дожидаемся пока все конекты будут закрыты
    """
    await app.messaging_pool_subscription.close()
    await app.messaging_pool_publish.close()

    await app.messaging_pool_subscription.wait_closed()
    await app.messaging_pool_publish.wait_closed()


@app.listener('after_server_start')
async def subscribe_to_channels_in_receiver(app, loop):
    """
    После того как сервер запущен, оформляем подписку на сообщения в каналах
    """
    await app.receiver.listening_channel()


@app.route('/')
async def test(request):
    return json({'hello': 'world'})


app.add_websocket_route(WsRoom.as_view(), '/room/<room_id>')

if __name__ == '__main__':
    signal(SIGINT, lambda s, f: app.stop())
    try:
        app.run(host='0.0.0.0', port=9100)
    except Exception:
        pass

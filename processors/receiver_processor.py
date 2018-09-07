from aioredis import RedisError
from aioredis.abc import AbcChannel
from aioredis.pubsub import Receiver
from models.room import Room


class ReceiverProcessor:
    def __init__(self, app):
        self.receiver = Receiver()
        self.messaging_pool = app.messaging_pool_subscription
        self.rooms = {}

    async def unsubscribe_channel(self, channel):
        """отписка с канала"""
        try:
            await self.messaging_pool.unsubscribe(channel)
        except RedisError as connError:
            pass
        except TypeError as typeError:
            pass
        except ValueError as valueError:
            pass

    async def subscribe_to_channel(self, channel):
        """подписаться на сообщения в канале"""
        try:
            await self.messaging_pool.subscribe(self.receiver.channel(channel))
        except RedisError as redisError:
            pass
        pass

    async def add_room(self, room: Room):
        """Сохраним в стостояние ресивера новую комнату (канал)"""
        if self.rooms.get(room.channel, None) is None:
            self.rooms[room.channel] = room

    async def rm_room(self, key):
        """После того как отписались от сообщений в канале,
         комната нам в состоянии Ресивера уже не нужну, удаляем ее"""
        del self.rooms[key]

    async def getRoom(self, room_key):
        """Ищем комнату уже зарегистрированную в
        ресивере, если нет то возвращаем None"""
        return self.rooms.get(room_key, None)

    async def listening_channel(self):
        await self.messaging_pool.subscribe(
            self.receiver.channel('system:unsubscribe')
        )
        """обработка сообщения в канале подписки"""
        async for channel, msg in self.receiver.iter():
            assert isinstance(channel, AbcChannel)
            if channel.name == b'system:unsubscribe':
                await self.messaging_pool.unsubscribe(msg)
                await self.rm_room(msg.decode('utf-8'))
            else:
                peer = self.rooms.get(channel.name.decode('utf-8'), None)
                if peer is not None:
                    await peer.broadcast(msg)

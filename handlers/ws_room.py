from sanic.views import HTTPMethodView

from models.room import Room


class WsRoom(HTTPMethodView):
    async def get(self, request, ws, room_id):
        _app = request.app
        channel_name = "room:{}".format(room_id)
        channel_name_str = "room:{}".format(room_id)
        room = await _app.receiver.getRoom(channel_name_str)
        if room is None:
            room = Room(room=room_id, sys_pub=_app.messaging_pool_publish)
            await _app.receiver.add_room(room)
        await room.add_ws(ws=ws)

        """Подписываемся на канал"""
        await  _app.receiver.subscribe_to_channel(channel_name)
        try:
            with await _app.messaging_pool_publish as conn:
                await conn.publish(channel_name_str, '@user has Joined chat')
            async for message in ws:
                with await _app.messaging_pool_publish as conn:
                    await conn.publish(channel_name_str, message)
        finally:
            ws.close()
            with await _app.messaging_pool_publish as conn:
                await conn.publish(channel_name_str, '@user has left chat')
            await room.remove_ws(ws=ws)

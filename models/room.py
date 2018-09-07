import websockets


class Room(object):
    channel = None
    room_id = None
    ws = set()

    def __init__(self, room, sys_pub):
        self.room_id = room
        self.channel = "room:{}".format(room)
        self.system_pub = sys_pub

    async def add_ws(self, ws):
        self.ws.add(ws)

    async def remove_ws(self, ws):
        try:
            self.ws.remove(ws)
            if len(self.ws) == 0:
                self.system_pub.publish('system:unsubscribe', self.channel)
        except KeyError:
            pass

    async def clear_all(self):
        self.ws.clear()

    async def broadcast(self, msg):
        """Рассылаем всем аффилированным сокетам сообщение."""
        for peer in self.ws:
            try:
                await peer.send(msg.decode('utf-8'))
            except websockets.exceptions.ConnectionClosed:
                await self.remove_ws(ws=peer)

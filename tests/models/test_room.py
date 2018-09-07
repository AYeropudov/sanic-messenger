from unittest import mock
import pytest
from models.room import Room


@pytest.fixture()
def resource():
    publisher = mock.Mock()
    test = Room(sys_pub=publisher, room='test')
    yield test


class TestRoom(object):
    def test_room_init(self, resource):
        room = resource
        assert room.room_id == 'test'
        assert room.ws == set()

    @pytest.mark.asyncio
    async def test_room_add_ws(self, resource):
        room = resource
        await room.add_ws('test_ws')
        assert room.ws == {'test_ws',}
        assert 1 == len(room.ws)
        assert not room.system_pub.publish.called

    @pytest.mark.asyncio
    async def test_room_remove_ws(self, resource):
        __new_room = resource
        await __new_room.add_ws('test2_ws')
        assert __new_room.ws == {'test_ws', 'test2_ws',}
        assert 2 == len(__new_room.ws)
        await __new_room.remove_ws('test_ws')
        assert __new_room.ws == {'test2_ws',}
        __new_room.system_pub.publish.assert_not_called()
        assert 1 == len(__new_room.ws)

    @pytest.mark.asyncio
    async def test_room_unsubscribe_empty_room(self, resource):
        __new_room = resource
        await __new_room.remove_ws('test2_ws')
        assert __new_room.system_pub.publish.called
        assert 0 == len(__new_room.ws)


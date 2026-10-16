from plugin.mixin import wrap
from plugin.runtime import Extension


@wrap('MSFSConnect')
def connect(_wrap, self):
    is_connected = _wrap(self)
    if not is_connected:
        from data import registry

        msg_box = registry.get('message_box')
        if msg_box:
            msg_box.info(
                title='Connection Unavailable',
                text='The Microsoft Flight Simulator connection is unavailable\n微软模拟飞行连接不可用\nMSFS 연결을 사용할 수 없습니다\nMicrosoft Flight Simulator bağlantısı kullanılamıyor',
            )
    return is_connected


class Plugin(Extension):
    id = 'msfs_disabled'
    name = 'MSFS Disabled'

    def setup(self, runtime):
        self.runtime = runtime

    def teardown(self):
        pass
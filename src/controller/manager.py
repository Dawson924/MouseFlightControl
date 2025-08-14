class ControllerManager:
    def __init__(self):
        self.controllers = {}
        self.metadata = {}

    def register(self, id, controller_class, metadata=None):
        """注册一个新的控制器"""
        self.controllers[id] = controller_class
        self.metadata[id] = metadata or {}

    def get_class(self, id):
        """获取控制器类"""
        return self.controllers.get(id)

    def get_metadata(self, id):
        """获取控制器的元数据"""
        return self.metadata.get(id, {})

    def get_name(self, id):
        metadata = self.get_metadata(id)
        return metadata['name']

    def ids(self):
        """获取所有注册的控制器名称"""
        return list(self.controllers.keys())

    def names(self):
        return [item['name'] for item in self.metadata.values()]

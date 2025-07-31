class ControllerManager:
    def __init__(self):
        self.controllers = {}
        self.metadata = {}

    def register(self, name, controller_class, metadata=None):
        """注册一个新的控制器"""
        self.controllers[name] = controller_class
        self.metadata[name] = metadata or {}

    def get_class(self, name):
        """获取控制器类"""
        return self.controllers.get(name)

    def get_metadata(self, name):
        """获取控制器的元数据"""
        return self.metadata.get(name, {})

    def names(self):
        """获取所有注册的控制器名称"""
        return list(self.controllers.keys())

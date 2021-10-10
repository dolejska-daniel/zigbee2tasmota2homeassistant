

class Entity:

    class Meta:
        is_valid: bool = False

    class TopicMeta:
        component: str = None
        node_id: str = None
        object_id: str = None

    def __init__(self):
        self.meta = self.Meta()
        self.topic_meta = self.TopicMeta()

    def serializable_data(self):
        return {k: v for k, v in self.__dict__.items() if k not in ("meta", "topic_meta")}

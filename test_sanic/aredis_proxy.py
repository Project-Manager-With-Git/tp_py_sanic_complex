from typing import Optional, Any
from pyproxypattern import Proxy
from aredis import StrictRedis


class AredisProxy(Proxy):
    """aredis的代理类."""
    __slots__ = ('instance', "_callbacks", "_instance_check", "url")

    def __init__(self, url: Optional[str] = None, decode_responses: bool = True, **kwargs: Any) -> None:
        if url:
            instance = self.new_instance(url, decode_responses, **kwargs)
            super().__init__(instance)
        else:
            super().__init__()

    def new_instance(self, url: str, decode_responses: bool, **kwargs: Any) -> Any:
        self.url = url
        return StrictRedis.from_url(url, decode_responses=decode_responses, **kwargs)

    def initialize_from_url(self, url: str, *, decode_responses: bool = False, **kwargs: Any) -> None:
        """初始化."""
        instance = self.new_instance(url, decode_responses, **kwargs)
        self.initialize(instance)


redis = AredisProxy()

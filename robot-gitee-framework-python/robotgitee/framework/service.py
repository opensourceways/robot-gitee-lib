from robotgitee.framework.dispatcher import _Dispatcher
from robotgitee.framework.handlers import _Handlers


def run(robot: object, port: int, timeout: int) -> None:
    h = _Handlers()
    h.register_handler(robot)

    hs = h.get_handlers()
    if len(hs) == 0:
        raise Exception("it is not a robot")

    d = _Dispatcher(('', port), hs)
    d.run()

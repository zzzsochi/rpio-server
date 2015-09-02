import asyncio
import enum
import logging


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


__all__ = ['Mode', 'Pull', 'Level', 'Status', 'RpioClient']


class Mode(enum.Enum):
    """ Pin mode, used in Pin.set_mode
    """
    input = 1
    output = 2


class Pull(enum.IntEnum):
    """ Pin mode, used in Pin.set_pull
    """
    off = 0
    down = 1
    up = 2


class Level(enum.IntEnum):
    """ Pin mode, returned from Pin.read
    """
    low = 0
    high = 1


class Status(enum.IntEnum):
    """ Used for RpioClient.status
    """
    disconnected = 0
    connected = 1


class _RpioClientProtocol(asyncio.Protocol):
    def __init__(self, client):
        self._client = client

    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        log.debug('connection to {}'.format(peername))
        self._transport = transport

    def data_received(self, data):
        log.debug('data received: {!r}'.format(data.decode()))
        self._client._received_data.put_nowait(data.strip())

    def connection_lost(self, exc):
        log.debug('connection lost')
        self._client.status = Status.disconnected

        if exc is not None:
            log.error('connection lost exc: {!r}'.format(exc))


class RpioClient:
    """ Client for rpio-server
    """
    status = Status.disconnected

    def __init__(self, loop):
        self._loop = loop
        self._lock = asyncio.Lock(loop=loop)
        self._received_data = asyncio.Queue(maxsize=1, loop=loop)

    @asyncio.coroutine
    def connect(self, host='localhost', port=1382):
        """ Connect to rpio-server
        """
        _pf = lambda: _RpioClientProtocol(self)
        try:
            t, p = yield from self._loop.create_connection(_pf, host, port)
        except OSError as exc:
            log.error(str(exc))
            raise exc

        self._transport = t
        self._protocol = p
        self.status = Status.connected
        log.debug('connected to {}:{}'.format(host, port))
        return (t, p)

    @asyncio.coroutine
    def close(self):
        """ Close connection
        """
        yield from self.send('close')

    def get_pin(self, num):
        """ Get pin instance
        """
        return Pin(self, num)

    @asyncio.coroutine
    def send(self, command, num=None):
        """ Send commands to server manually
        """
        if self.status != Status.connected:
            log.error("client is disconnected")
            raise RuntimeError("client is disconnected")

        with (yield from self._lock):
            if num is not None:
                data = '{} {}\n'.format(command, num)
            else:
                data = command + '\n'

            self._transport.write(data.encode('utf8'))
            log.debug('command sent: {!r}'.format(data))

            resp = ''
            while resp or self.status == Status.connected:
                try:
                    resp = self._received_data.get_nowait()
                except asyncio.queues.QueueEmpty:
                    yield from asyncio.sleep(0.001)

        return resp


class Pin:
    """ Pin object
    """
    def __init__(self, client, num):
        self._client = client
        self.num = num

    def __repr__(self):
        return '<Pin {}>'.format(self.num)

    @asyncio.coroutine
    def _send(self, command):
        yield from self._client.send(command, self.num)

    @asyncio.coroutine
    def set_mode(self, mode):
        """ Set pin's mode

        Input Mode enumerate.
        """
        if mode == Mode.input:
            yield from self._send('input')
        elif mode == Mode.output:
            yield from self._send('output')
        else:
            raise TypeError("bad mode")

    @asyncio.coroutine
    def set_pull(self, pull_mode):
        """ Set pulling

        Input Pull enumerate.
        """
        if pull_mode == Pull.off:
            yield from self._send('pulloff')
        elif pull_mode == Pull.up:
            yield from self._send('pullup')
        elif pull_mode == Pull.down:
            yield from self._send('pulldown')
        else:
            raise TypeError("bad pull mode")

    @asyncio.coroutine
    def read(self):
        """ Read pin state

        Return Level instance.
        """
        resp = yield from self._send('read')

        if resp == '0':
            return Level.low
        elif resp == '1':
            return Level.high
        else:
            raise RuntimeError("bad response")

    @asyncio.coroutine
    def low(self):
        """ Set pin state to low
        """
        yield from self._send('low')

    @asyncio.coroutine
    def high(self):
        """ Set pin state to high
        """
        yield from self._send('high')

    @asyncio.coroutine
    def toggle(self):
        """ Toggle pin state
        """
        yield from self._send('toggle')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def main(loop):
        client = RpioClient(loop)
        yield from client.connect()
        # pin = client.get_pin(13)
        # yield from pin.set_mode(Mode.input)
        yield from client.close()

    loop.run_until_complete(main(loop))

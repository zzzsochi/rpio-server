rpio-client
===========

Python client library for `rpio-server <https://github.com/zzzsochi/rpio-server>`_.

Installation
------------

.. code:: shell

    pip install rpio-client

API
---

All API in one example:

.. code:: python

    import asyncio
    from rpio_client import *

    @asyncio.coroutine
    def main(loop):
        client = RpioClient(loop)  # create client
        yield from client.connect()  # connect to server

        pin = client.get_pin(13)  # get pin 13 instance
        yield from pin.set_mode(Mode.input)  # set input mode
        yield from pin.set_pull(Pull.down)  # set pulling to ground
        print(yield from pin.read())  # print state on pin 13

        # blinking
        pin = client.get_pin(10)
        pin.set_mode(Mode.output)
        for _ in range(10):
            yield from pin.toggle()
            yield from asyncio.sleep(1)

        yield from client.close()  # close connection

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))

rpio-server
===========

Standalone server application to control GPIO on RaspberryPi.

Problem
-------

For work with GPIO needs r/w access to `/dev/mem`, but only root have this. Start users's applications as root is bad idea. Very bad. Yes, I'm paranoid.

Why Go
------

Go easy crosscompile standalone application. That is all.

Building
--------

.. code:: shell

    make compile

Create `rpio-server` binary for arm linux, for run on RaspberryPi. For building I'm using OSX.

Starting
--------

For this process needs reed and write access to `/dev/mem`.

.. code:: shell

    sudo ./rpio-server

By default server listen *127.0.0.1:1382*. Use `--ip` command argument for change this.

.. code:: shell

    sudo ./rpio-server --ip 0.0.0.0:1382

API
---

API is very simply! Use telnet, Luke!

**Setting pin mode**

*"<pin>" is decimal number of pin.*

input <pin>
  Set input mode. Use *read* for read pin's state.
  Response "ok".

output <pin>
  Set output mode. Use *high*, *low* and *toggle*.
  Response "ok".

**Pulling**

pullup <pin>
  Set pulling to high.
  Response "ok".

pulldown <pin>
  Set pulling to ground.
  Response "ok".

pulloff <pin>
  Disable pulling.
  Response "ok".

**Operations**

read <pin>
  Read pin's state. Response is "0" or "1".

high <pin>
  Set pin state to high. Used only in *output* mode.
  Response "ok".

low <pin>
  Set pin state to low.
  Response "ok".

toggle <pin>
  Toggle pin state.
  Response "ok".

**Close**

close
  Close connection from server.
  Response "bye".

**Example telnet log**

::

    input 13
    ok
    pulldowm 13
    ok
    read 13
    0
    pullup 13
    ok
    read 13
    1
    pulloff 13
    ok
    output 13
    ok
    high 13
    ok
    close
    bye

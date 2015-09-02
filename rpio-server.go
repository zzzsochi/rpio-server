/*
Server for simple control the RaspberryPi GPIO pins.

Commands may be usable from telnet:

    input <pin>
    read <pin>

    output <pin>
    high <pin>
    low <pin>
    toggle <pin>

    pullup <pin>
    pulldown <pin>
    pulloff <pin>

    close
*/

package main

import (
    "errors"
    "fmt"
    "flag"
    "net"
    "strings"
    "strconv"
    "log"
    "github.com/stianeikeland/go-rpio"
)

type Command struct {
    name string
    pin uint8
}

func processCommand(command Command) (response string) {
    pin := rpio.Pin(command.pin)

    switch command.name {
    case "input", "in":
        pin.Input()
        response = "ok"

    case "output", "out":
        pin.Output()
        response = "ok"

    case "pullup", "pu":
        pin.PullUp()
        response = "ok"

    case "pulldown", "pd":
        pin.PullDown()
        response = "ok"

    case "pulloff", "po":
        pin.PullOff()
        response = "ok"

    case "high", "h":
        pin.High()
        response = "ok"

    case "low", "l":
        pin.Low()
        response = "ok"

    case "toggle", "t":
        pin.Toggle()
        response = "ok"

    case "read", "r":
        res := pin.Read()
        switch res {
        case rpio.Low:
            response = "0"
        case rpio.High:
            response = "1"
        default:
            response = "unknown"
        }
    default:
        response = fmt.Sprintf("Unknown command: \"%s\"", command.name)
    }
    return
}


func processLine(line string) (command Command, err error) {
    switch line {
    case "close":
        command.name = "close"
    default:
        parsed := strings.Split(line, " ")
        if len(parsed) != 2 {
            err = errors.New(fmt.Sprintf("parse error \"%s\"", line))
            return
        }

        pin, pin_err := strconv.Atoi(parsed[1])
        if pin_err != nil {
            err = errors.New(fmt.Sprintf("bad pin number \"%s\"", parsed[1]))
            return
        }

        command.name = parsed[0]
        command.pin = uint8(pin)
    }
    return
}


func readLine(conn net.Conn) (line string, err error) {
    buf := make([]byte, 0, 100)
    for {
        b := make([]byte, 1)
        n, er := conn.Read(b)

        if n > 0 {
            c := b[0]
            if c == '\n' || c == '\r' { // end of line
                line = string(buf)
                if len(line) == 0 {
                    continue
                } else {
                    break
                }
            }
            buf = append(buf, c)
        }

        if er != nil {
            err = er
            line = string(buf)
            return
        }
    }

    line = string(buf)
    return
}


func handleConnection(conn net.Conn) {
    log.Printf("Connection %s", conn.RemoteAddr())

    defer conn.Close()

    var line, response string
    var err error
    var command Command

    for {
        line, err = readLine(conn)
        if err != nil {
            conn.Write([]byte(fmt.Sprintf("Error: %s\n", err)))
            break
        }

        command, err = processLine(line)
        if err != nil {
            conn.Write([]byte(fmt.Sprintf("Error: %s\n", err)))
            // break
        } else if command.name == "close" {
            log.Printf("Close %s", conn.RemoteAddr())
            conn.Write([]byte("bye\n"))
            return
        } else {
            response = processCommand(command)
            conn.Write([]byte(response))
            conn.Write([]byte("\n"))
        }
    }
}


func openRpio() {
    rpio_err := rpio.Open()
    if rpio_err != nil {
        log.Fatal(rpio_err)
    }
    log.Print("Open /dev/mem")
}


func startServer(ip string) {
    listener, err := net.Listen("tcp", ip)
    if err != nil {
        log.Fatal(err)
    }
    defer listener.Close()

    log.Printf("Listening %s", listener.Addr())

    for {
        // Wait for a connection.
        conn, err := listener.Accept()
        if err != nil {
            log.Fatal(err)
        } else {
            go handleConnection(conn)
        }
    }
}


func main() {
    ip := flag.String("ip", "127.0.0.1:1382", "host and port for listeting")
    flag.Parse()

    openRpio()
    defer rpio.Close()

    startServer(*ip)
}

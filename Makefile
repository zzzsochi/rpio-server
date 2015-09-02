.PHONY: help
# target: help - Display callable targets
help:
	@egrep "^# target:" [Mm]akefile | sed -e 's/^# target: //g' | sort


clean:
	rm -f ./rpio-server
	rm -rf ./lib


lib:
	mkdir -p lib/src/github.com/stianeikeland/
	cd lib/src/github.com/stianeikeland/; git clone https://github.com/stianeikeland/go-rpio.git


.PHONY: compile
# target: compile - Compile Go code
compile: lib
	GOPATH=`pwd`/lib CC=arm-linux-gnueabihf-gcc GOOS=linux GOARCH=arm GOARM=6 go build -v -o rpio-server -ldflags="-extld=$CC"


.PHONY: run
# target: run - Run server without compiling
run: lib
	GOPATH=`pwd`/lib go run go-rpio-server.go

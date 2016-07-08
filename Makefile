.PHONY: help
# target: help - Display callable targets
help:
	@egrep "^# target:" [Mm]akefile | sed -e 's/^# target: //g' | sort


clean:
	rm -rf ./build


lib:
	GOPATH=`pwd`/build GOBIN=`pwd`/bin go get


.PHONY: compile
# target: compile - Compile Go code
pi:
	GOPATH=`pwd`/build CC=arm-linux-gnueabihf-gcc GOOS=linux GOARCH=arm GOARM=6 go build -v -o build/rpio-server -ldflags="-extld=$CC"

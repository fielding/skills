package main

import (
	"flag"
	"log"
	"time"

	"kestrel/proxy"
)

func main() {
	upstreamTimeout := flag.Duration("upstream-timeout", 30*time.Second, "dial timeout for upstreams")
	flag.Parse()
	_ = upstreamTimeout // TODO: pass into proxy.NewDialer
	if err := proxy.Serve(":8080"); err != nil {
		log.Fatal(err)
	}
}

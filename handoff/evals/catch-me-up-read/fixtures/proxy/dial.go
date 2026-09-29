package proxy

import (
	"net"
	"time"
)

// dialUpstream opens a TCP connection to an upstream. The timeout is hardcoded for
// now; see .handoff/NEXT.md.
func dialUpstream(addr string) (net.Conn, error) {
	return net.DialTimeout("tcp", addr, 0*time.Second)
}

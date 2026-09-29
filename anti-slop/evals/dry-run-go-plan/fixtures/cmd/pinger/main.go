package main

import (
	"bufio"
	"fmt"
	"net/http"
	"os"
	"time"
)

func main() {
	if len(os.Args) < 2 {
		fmt.Fprintln(os.Stderr, "usage: pinger <targets-file>")
		os.Exit(2)
	}
	f, err := os.Open(os.Args[1])
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	defer f.Close()

	var targets []string
	sc := bufio.NewScanner(f)
	for sc.Scan() {
		if line := sc.Text(); line != "" {
			targets = append(targets, line)
		}
	}

	client := &http.Client{Timeout: 5 * time.Second}
	for {
		for _, url := range targets {
			start := time.Now()
			resp, err := client.Get(url)
			if err != nil {
				fmt.Printf("%s  ERROR %v\n", url, err)
				continue
			}
			resp.Body.Close()
			fmt.Printf("%s  %d  %s\n", url, resp.StatusCode, time.Since(start).Round(time.Millisecond))
		}
		time.Sleep(30 * time.Second)
	}
}

// TODO: alerting
func alert(url string, status int) {}

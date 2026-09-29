# kestrel

Small HTTP reverse proxy for internal services. Go 1.23. See `.handoff/` for the
current working notes.

    make build
    make test        # go test ./... -count=1
    make deploy-staging

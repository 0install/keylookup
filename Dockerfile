FROM ocurrent/opam:alpine-3.10 AS build
RUN cd opam-repository && git pull && opam update
RUN opam depext -i cohttp-lwt-unix astring xmlm dune
COPY --chown=opam:opam . /src
WORKDIR /src
RUN opam exec -- dune build main.exe

FROM alpine:3.10
RUN apk add --no-cache dumb-init
COPY index.html debian.db debian-maintainers.db /srv/
WORKDIR /srv
COPY --from=build /src/_build/default/main.exe /usr/bin/0install-key-lookup
CMD ["dumb-init", "/usr/bin/0install-key-lookup"]

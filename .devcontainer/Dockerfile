# ################################################################################
#  Copyright (c) 2025  Claudio André <portfolio-2025br at claudioandre.slmail.me>
#              ___                _      ___       _
#             (  _`\             ( )_  /'___)     (_ )  _
#             | |_) )  _    _ __ | ,_)| (__   _    | | (_)   _
#             | ,__/'/'_`\ ( '__)| |  | ,__)/'_`\  | | | | /'_`\
#             | |   ( (_) )| |   | |_ | |  ( (_) ) | | | |( (_) )
#             (_)   `\___/'(_)   `\__)(_)  `\___/'(___)(_)`\___/'
#
# This program comes with ABSOLUTELY NO WARRANTY; express or implied.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, as expressed in version 2, seen at
# https://www.gnu.org/licenses/gpl-2.0.html
# ################################################################################
# Dockerfile for development with Python
# More info at https://github.com/portfolio-2025br/bootcamp-python

FROM mcr.microsoft.com/devcontainers/python:3@sha256:0aa711e570b306c02946cdda67587ce8c65978dbb65691341cbcfd4854dfcfff

ENV NODE_DOWNLOAD_SHA256="c61e58b2284efea4746ffbdcb4d4080f58fa7a31fb0060d2b024eb3d2e95572d"

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    # Node
    && TMPFILE=$(mktemp /tmp/node-XXXXX) \
    && curl -sSf --proto '=https' --tlsv1.3 https://deb.nodesource.com/setup_22.x | \
        tee "$TMPFILE" | bash - \
    && echo "$NODE_DOWNLOAD_SHA256  $TMPFILE" | sha256sum -c - \
    && apt-get -y install --no-install-recommends nodejs=* \
    # Clean up
    && apt-get -y clean \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*

HEALTHCHECK NONE

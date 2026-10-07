# The Home Assistant app image: the ShellyLanMan release image plus an entry
# script. ShellyLanMan itself is unchanged and runs as its own user (10001).
ARG SHELLYLANMAN_VERSION=0.9.5
FROM ghcr.io/wimmme/shellylanman:${SHELLYLANMAN_VERSION}

USER root
# su-exec: drop from root (needed once to own /data, which the Supervisor
# mounts as root) to the shellylanman user.
RUN apk add --no-cache su-exec
COPY run.sh /run.sh
RUN chmod 0755 /run.sh

# The image's HEALTHCHECK (shellylanman -healthcheck, which reads the port in use
# from /data/listen.port, so it follows the option "port") stays: the Supervisor waits for "healthy" before the app counts
# as started, and its watchdog restarts an unhealthy app. "HEALTHCHECK NONE"
# would leave the app in "startup" for ever.

ARG SHELLYLANMAN_VERSION
LABEL io.hass.name="ShellyLanMan" \
      io.hass.description="Discover, monitor and manage the Shelly devices on your LAN" \
      io.hass.type="addon" \
      io.hass.version="${SHELLYLANMAN_VERSION}" \
      org.opencontainers.image.source="https://github.com/wimmme/shellylanman-ha" \
      org.opencontainers.image.licenses="GPL-3.0-or-later"

ENTRYPOINT ["/run.sh"]

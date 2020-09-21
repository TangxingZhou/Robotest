FROM python:alpine

ARG ALLURE_RELEASE=2.13.5
ARG ALLURE_REPO=https://dl.bintray.com/qameta/maven/io/qameta/allure/allure-commandline

WORKDIR /usr/app/test

COPY requirements.txt /tmp

RUN \
    sed -i 's/\/\/[^\/]*/\/\/mirrors.aliyun.com/g' /etc/apk/repositories \
    && apk --no-cache update \
    && apk --no-cache upgrade \
    && apk --no-cache add gcc libffi-dev openssh openssl-dev make sqlite sqlite-dev mysql-dev unixodbc-dev build-base tzdata bash sshpass curl git \
    && cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && echo "Asia/Shanghai" > /etc/timezone \
    && mkdir -p /root/.ssh \
    && echo "StrictHostKeyChecking accept-new" > /root/.ssh/config \
    && pip install -r /tmp/requirements.txt \
    && rm -rf ~/.cache/pip

RUN apk add --no-cache java-cacerts

ENV JAVA_HOME /opt/openjdk-16
ENV PATH $JAVA_HOME/bin:$PATH

# https://jdk.java.net/
# >
# > Java Development Kit builds, from Oracle
# >
ENV JAVA_VERSION 16-ea+5
# "For Alpine Linux, builds are produced on a reduced schedule and may not be in sync with the other platforms."

RUN set -eux; \
        \
        arch="$(apk --print-arch)"; \
# this "case" statement is generated via "update.sh"
        case "$arch" in \
# amd64
                x86_64) \
                        downloadUrl=https://download.java.net/java/early_access/alpine/5/binaries/openjdk-16-ea+5_linux-x64-musl_bin.tar.gz; \
                        downloadSha256=1ec940bea148a7ececda635c209de3836fe4e6511f5d49d4248cf6d52c77aac8; \
                        ;; \
# fallback
                *) echo >&2 "error: unsupported architecture: '$arch'"; exit 1 ;; \
        esac; \
        \
        wget -O openjdk.tgz "$downloadUrl"; \
        echo "$downloadSha256 *openjdk.tgz" | sha256sum -c -; \
        \
        mkdir -p "$JAVA_HOME"; \
        tar --extract \
                --file openjdk.tgz \
                --directory "$JAVA_HOME" \
                --strip-components 1 \
                --no-same-owner \
        ; \
        rm openjdk.tgz; \
        \
# see "java-cacerts" package installed above (which maintains "/etc/ssl/certs/java/cacerts" for us)
        rm -rf "$JAVA_HOME/lib/security/cacerts"; \
        ln -sT /etc/ssl/certs/java/cacerts "$JAVA_HOME/lib/security/cacerts"; \
        \
# https://github.com/docker-library/openjdk/issues/212#issuecomment-420979840
# https://openjdk.java.net/jeps/341
        java -Xshare:dump; \
        \
# basic smoke test
        javac --version; \
        java --version

# "jshell" is an interactive REPL for Java (see https://en.wikipedia.org/wiki/JShell)
# CMD ["jshell"]

RUN \
    && curl ${ALLURE_REPO}/${ALLURE_RELEASE}/allure-commandline-${ALLURE_RELEASE}.zip -L -o /tmp/allure-commandline.zip \
    && unzip -q /tmp/allure-commandline.zip -d /root \
    && ln -sf /root/allure-$ALLURE_RELEASE/bin/allure /usr/local/bin/allure \
    && apk del unzip \
    && rm -rf /tmp/*

ENV ALLURE_HOME=/root/allure-$ALLURE_RELEASE
# ENV ALLURE_HOME_SL=/allure
# ENV PATH=$PATH:$ALLURE_HOME/bin

ENV PORT=5050
EXPOSE $PORT
HEALTHCHECK --interval=10s --timeout=60s --retries=3 \
      CMD curl -f http://localhost:$PORT || exit 1

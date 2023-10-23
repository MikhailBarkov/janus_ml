FROM debian:buster-slim as builder

ARG TARGETARCH
ARG JANUS_VERSION=1.0.0-rc1
ARG YQ_VERSION=3.4.1

ENV JANUS_VERSION=${JANUS_VERSION} \
    JANUS_HOME=/opt/janusgraph

WORKDIR /opt

RUN apt update -y && apt install -y gpg unzip curl && \
    curl -fSL https://github.com/JanusGraph/janusgraph/releases/download/v${JANUS_VERSION}/janusgraph-${JANUS_VERSION}.zip -o janusgraph.zip && \
    curl -fSL https://github.com/JanusGraph/janusgraph/releases/download/v${JANUS_VERSION}/janusgraph-${JANUS_VERSION}.zip.asc -o janusgraph.zip.asc && \
    curl -fSL https://github.com/JanusGraph/janusgraph/releases/download/v${JANUS_VERSION}/KEYS -o KEYS && \
    curl -fSL https://github.com/mikefarah/yq/releases/download/${YQ_VERSION}/yq_linux_${TARGETARCH} -o yq && \
    gpg --import KEYS && \
    gpg --batch --verify janusgraph.zip.asc janusgraph.zip && \
    unzip janusgraph.zip && \
    mv janusgraph-${JANUS_VERSION} /opt/janusgraph && \
    rm -rf ${JANUS_HOME}/elasticsearch && \
    rm -rf ${JANUS_HOME}/javadocs && \
    rm -rf ${JANUS_HOME}/log && \
    rm -rf ${JANUS_HOME}/examples && \
    rm -rf ${JANUS_HOME}/conf/janusgraph-*.properties && \
    mv ${JANUS_HOME}/conf/gremlin-server/gremlin-server.yaml ${JANUS_HOME}/conf/janusgraph-server.yaml && \
    rm -rf ${JANUS_HOME}/conf/gremlin-server

COPY conf/ ${JANUS_HOME}/conf/
COPY scripts/remote-connect.groovy ${JANUS_HOME}/scripts/
COPY conf/gremlin-server/gremlin-server.yaml ${JANUS_HOME}/conf/janusgraph-server.yaml

FROM maven:3.6.0-jdk-8-slim as java_builder

COPY /predictplugin/ /predictplugin/
RUN mvn -f ${JANUS_HOME}/predictplugin/pom.xml package

FROM eclipse-temurin:8-jre

ARG CREATED=test
ARG REVISION=test
ARG JANUS_VERSION=1.0.0-rc1

ENV JANUS_VERSION=${JANUS_VERSION} \
    JANUS_HOME=/opt/janusgraph \
    JANUS_CONFIG_DIR=/etc/opt/janusgraph \
    JANUS_DATA_DIR=/var/lib/janusgraph \
    JANUS_SERVER_TIMEOUT=300 \
    JANUS_STORAGE_TIMEOUT=600 \
    JANUS_PROPS_TEMPLATE=berkeleyje \
    JANUS_INITDB_DIR=/docker-entrypoint-initdb \
    JANUS_EXT_DIR=/opt/janusgraph/ext \
    JANUS_LIB_DIR=/opt/janusgraph/lib/ \
    gremlinserver.graphs.graph=/etc/opt/janusgraph/janusgraph.properties \
    gremlinserver.threadPoolWorker=1 \
    gremlinserver.gremlinPool=8

RUN groupadd -r janusgraph --gid=999 && \
    useradd -r -g janusgraph --uid=999 -d ${JANUS_DATA_DIR} janusgraph && \
    apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends krb5-user && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/janusgraph/ /opt/janusgraph/
COPY --from=builder /opt/yq /usr/bin/yq
COPY --from=java_builder /predictplugin/target/janusgraph-predictplugin-0.0.1.jar ${JANUS_LIB_DIR}/janusgraph-predictplugin-0.0.1.jar
COPY docker-entrypoint.sh /usr/local/bin/
COPY load-initdb.sh /usr/local/bin/
COPY conf/gremlin-server/gremlin-server.yaml ${JANUS_CONFIG_DIR}/janusgraph-server.yaml
COPY conf/gremlin-server/services.yaml ${JANUS_CONFIG_DIR}/services.yaml
COPY ${JANUS_INITDB_DIR}/upload_cora.groovy ${JANUS_INITDB_DIR}/upload_cora.groovy
COPY ${JANUS_INITDB_DIR}/data/cora_nodes.csv ${JANUS_HOME}/dataset/cora_nodes.csv
COPY ${JANUS_INITDB_DIR}/data/cora_edges.csv ${JANUS_HOME}/dataset/cora_edges.csv
COPY ${JANUS_INITDB_DIR}/data/FA-KES-Dataset.csv ${JANUS_HOME}/dataset/FA-KES-Dataset.csv


RUN chmod 755 /usr/local/bin/docker-entrypoint.sh
RUN chmod 755 /usr/local/bin/load-initdb.sh
RUN chmod 755 /usr/bin/yq
RUN mkdir -p ${JANUS_INITDB_DIR} ${JANUS_CONFIG_DIR} ${JANUS_DATA_DIR} ${JANUS_EXT_DIR}
RUN chown -R janusgraph:janusgraph ${JANUS_HOME} ${JANUS_CONFIG_DIR} ${JANUS_DATA_DIR} ${JANUS_EXT_DIR} ${JANUS_INITDB_DIR}

EXPOSE 8182

WORKDIR ${JANUS_HOME}
USER janusgraph

ENTRYPOINT [ "docker-entrypoint.sh" ]
CMD [ "janusgraph" ]

LABEL org.opencontainers.image.title="JanusGraph Docker Image" \
      org.opencontainers.image.description="Official JanusGraph Docker image" \
      org.opencontainers.image.url="https://janusgraph.org/" \
      org.opencontainers.image.documentation="https://docs.janusgraph.org/v0.6/" \
      org.opencontainers.image.revision="${REVISION}" \
      org.opencontainers.image.source="https://github.com/JanusGraph/janusgraph-docker/" \
      org.opencontainers.image.vendor="JanusGraph" \
      org.opencontainers.image.version="${JANUS_VERSION}" \
      org.opencontainers.image.created="${CREATED}" \
      org.opencontainers.image.license="Apache-2.0"
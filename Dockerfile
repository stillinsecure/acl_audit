FROM alpine:3.4

# Update
RUN apk add --update python \
  python-dev \
  py-pip \
  gcc \
  jpeg-dev \
  zlib-dev \
  musl-dev \
  libffi-dev \
  openssl-dev \
  libxml2-dev \
  libxslt-dev

ENV LIBRARY_PATH=/lib:/usr/lib

# Dependencies
RUN pip install configargparse \
  mitmproxy \
  xlsxwriter

# Copy source
COPY *.py /opt/acl_audit/
COPY acl_audit.conf /opt/acl_audit/
COPY plugins/*.py /opt/acl_audit/plugins/

EXPOSE 8080

VOLUME /opt/acl_audit/output
WORKDIR /opt/acl_audit
ENTRYPOINT ["python", "acl_audit.py"]

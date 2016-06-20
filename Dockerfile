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
COPY *.py /src/
COPY acl_audit.conf /src/
COPY plugins/*.py /src/plugins/

# Mod filesystem
RUN mkdir /src/output
WORKDIR /src
CMD ["python", "/src/acl_audit.py"]

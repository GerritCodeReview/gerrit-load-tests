#!/bin/ash

CA_CERT="/var/loadtest/certs"

test -f $REQUESTS_CA_BUNDLE || touch $REQUESTS_CA_BUNDLE

if [ -d "$CA_CERT" ]; then
  for file in "$CA_CERT/"*; do
    (cat "$file"; echo) >> "$REQUESTS_CA_BUNDLE"
  done
fi

python3 ./start_test.py $@

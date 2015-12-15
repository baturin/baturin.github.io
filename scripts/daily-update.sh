#!/bin/bash

LISTINGS_DIR=/var/www/wvpoi.batalex.ru/listings
DUMPS_DIR=/var/www/wvpoi.batalex.ru/dumps/
cd /home/alexey/wikivoyage-listings/ && ./wikivoyage-listings.sh -daily-update -latest-count 5 -listings-dir "$LISTINGS_DIR" -dumps-cache-dir "$DUMPS_DIR"

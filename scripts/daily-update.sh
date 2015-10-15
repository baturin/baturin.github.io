#!/bin/bash

cd /home/alexey/wikivoyage-listings/ && ./wikivoyage-listings.sh -daily-update -latest-count 5 -listings-dir /var/www/wvpoi.batalex.ru/wikivoyage-poi -dumps-cache-dir /var/www/wvpoi.batalex.ru/wikivoyage-dumps/

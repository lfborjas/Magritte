#!/bin/bash
$PWD/scrapy-ctl.py crawl dmoz.org --logfile log
shutdown -h now

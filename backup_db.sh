#!/bin/bash

today=$(date +'%Y-%m-%d')
filename=/var/lib/postgresql/pdl_$today.sql

pg_dump -d pdl > $filename && bzip2 $filename

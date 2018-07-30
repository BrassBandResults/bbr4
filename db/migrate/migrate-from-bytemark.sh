#!/bin/bash
# expects a file in ~/bbr.sql which was exported with:
#  pg_dump bbr --no-owner --quote-all-identifiers --inserts > bbr.sql

psql -h bbr-db.csxjs9r4u4br.eu-west-2.rds.amazonaws.com -U bbradmin -d bbr -f prepare.sql
psql -h bbr-db.csxjs9r4u4br.eu-west-2.rds.amazonaws.com -U bbr -d bbr -f ~/bbr.sql
psql -h bbr-db.csxjs9r4u4br.eu-west-2.rds.amazonaws.com -U bbradmin -d bbr -f clearup.sql


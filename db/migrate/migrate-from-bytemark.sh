#!/bin/bash
sed -i 's/OWNER TO postgres/OWNER TO rds_superuser/g' ~/bbr.sql

psql -h bbr-db.csxjs9r4u4br.eu-west-2.rds.amazonaws.com -U bbradmin -d bbr -f prepare.sql
psql -h bbr-db.csxjs9r4u4br.eu-west-2.rds.amazonaws.com -U bbradmin -d bbr -v ON_ERROR_STOP=1 -f ~/bbr.sql


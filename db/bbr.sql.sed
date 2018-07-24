CREATE EXTENSION postgis;
CREATE EXTENSION fuzzystrmatch;
CREATE EXTENSION postgis_tiger_geocoder;
CREATE EXTENSION postgis_topology;

CREATE USER bbr WITH PASSWORD '2barsrepeat';

sed -i 's/OWNER TO postgres/OWNER TO rds_superuser/g' file.txt

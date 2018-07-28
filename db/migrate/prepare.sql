CREATE EXTENSION postgis;
CREATE EXTENSION fuzzystrmatch;
CREATE EXTENSION postgis_tiger_geocoder;
CREATE EXTENSION postgis_topology;

ALTER SCHEMA topology owner to rds_superuser;

CREATE USER bbr WITH PASSWORD '045003a0083366dea';
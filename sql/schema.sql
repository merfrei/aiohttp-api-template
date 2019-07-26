CREATE TABLE foo (
       id serial PRIMARY KEY,
       name varchar(1024) NOT NULL,
       active boolean DEFAULT true);

CREATE INDEX foo_name_ix ON foo (name);

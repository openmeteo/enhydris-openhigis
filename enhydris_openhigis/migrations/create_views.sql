CREATE SCHEMA IF NOT EXISTS openhigis AUTHORIZATION anton;

SET search_path TO openhigis, public;

/* Stations */

DROP VIEW IF EXISTS stations;

CREATE VIEW stations
    AS SELECT
        g.id,
        g.name,
        g.remarks,
        ST_Transform(g.geom, 2100) AS geom,
        gp.altitude,
        s.owner_id,
        s.is_automatic,
        s.start_date,
        s.end_date,
        s.overseer,
        s.copyright_years,
        s.copyright_holder
    FROM
        enhydris_gentity g
        INNER JOIN enhydris_gpoint gp ON gp.gentity_ptr_id = g.id
        INNER JOIN enhydris_station s ON s.gpoint_ptr_id = g.id;

/* Functions common to all tables */

CREATE OR REPLACE FUNCTION insert_into_gentity(NEW ANYELEMENT) RETURNS integer
AS $$
DECLARE gentity_id INTEGER;
BEGIN
    INSERT INTO enhydris_gentity (name, code, remarks, geom)
        VALUES (
            NEW.name,
            COALESCE(NEW.code, ''),
            COALESCE(NEW.remarks, ''),
            ST_Transform(NEW.geom, 4326)
        )
        RETURNING id INTO gentity_id;
    RETURN gentity_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION insert_into_garea(NEW ANYELEMENT) RETURNS integer
AS $$
DECLARE gentity_id INTEGER;
BEGIN
    SELECT openhigis.insert_into_gentity(NEW) INTO gentity_id;
    INSERT INTO enhydris_garea (gentity_ptr_id, category_id)
        VALUES (gentity_id, 1);
    RETURN gentity_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION update_gentity(OLD ANYELEMENT, NEW ANYELEMENT)
RETURNS void
AS $$
BEGIN
    UPDATE enhydris_gentity
        SET
            name=NEW.name,
            code=COALESCE(NEW.code, ''),
            remarks=COALESCE(NEW.remarks, ''),
            geom=ST_Transform(NEW.geom, 4326)
        WHERE id=OLD.id;
END;
$$ LANGUAGE plpgsql;

/* Water districts */

DROP VIEW IF EXISTS water_districts;

CREATE VIEW water_districts
    AS SELECT
        g.id,
        g.name,
        g.code,
        g.remarks,
        ST_Transform(g.geom, 2100) AS geom,
        wd.length,
        wd.area
    FROM
        enhydris_gentity g
        INNER JOIN enhydris_openhigis_waterdistrict wd ON wd.garea_ptr_id = g.id;

CREATE OR REPLACE FUNCTION insert_into_water_districts() RETURNS TRIGGER
AS $$
DECLARE gentity_id INTEGER;
BEGIN
    gentity_id = openhigis.insert_into_garea(NEW);
    INSERT INTO enhydris_openhigis_waterdistrict (garea_ptr_id, length, area)
        VALUES (gentity_id, NEW.length, NEW.area);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER water_districts_insert INSTEAD OF INSERT ON water_districts
    FOR EACH ROW EXECUTE PROCEDURE insert_into_water_districts();

CREATE OR REPLACE FUNCTION update_water_districts() RETURNS TRIGGER
AS $$
BEGIN
    PERFORM openhigis.update_gentity(OLD, NEW);
    UPDATE enhydris_openhigis_waterdistrict
        SET length=NEW.length, area=NEW.area
        WHERE garea_ptr_id=OLD.id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER water_districts_update INSTEAD OF UPDATE ON water_districts
    FOR EACH ROW EXECUTE PROCEDURE update_water_districts();

CREATE OR REPLACE FUNCTION delete_water_districts()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM enhydris_openhigis_waterdistrict WHERE garea_ptr_id=OLD.id;
    DELETE FROM enhydris_garea WHERE gentity_ptr_id=OLD.id;
    DELETE FROM enhydris_gentity WHERE id=OLD.id;
    RETURN OLD;
END;
$$;

CREATE TRIGGER water_districts_delete INSTEAD OF DELETE ON water_districts
    FOR EACH ROW EXECUTE PROCEDURE delete_water_districts();

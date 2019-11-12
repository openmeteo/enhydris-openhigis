CREATE SCHEMA IF NOT EXISTS openhigis;

SET search_path TO openhigis, public;

/* Stations */

DROP VIEW IF EXISTS stations;

CREATE VIEW station
    AS SELECT
        g.id,
        g.name,
        g.remarks,
        gs.geom2100 AS geometry,
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
        INNER JOIN enhydris_station s ON s.gpoint_ptr_id = g.id
        INNER JOIN enhydris_openhigis_station gs ON gs.station_ptr_id = g.id;

CREATE OR REPLACE FUNCTION update_station() RETURNS TRIGGER
AS $$
BEGIN
    UPDATE enhydris_openhigis_station SET geom2100=NEW.geometry
    WHERE station_ptr_id=OLD.id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER station_update
    INSTEAD OF UPDATE ON station
    FOR EACH ROW EXECUTE PROCEDURE update_station();

/* Functions common to all tables */

CREATE OR REPLACE FUNCTION insert_into_gentity(NEW ANYELEMENT) RETURNS integer
AS $$
DECLARE gentity_id INTEGER;
BEGIN
    INSERT INTO enhydris_gentity (name, code, remarks, geom)
        VALUES (
            COALESCE(NEW.geographicalName, ''),
            COALESCE(NEW.hydroId, ''),
            COALESCE(NEW.remarks, ''),
            ST_Transform(NEW.geometry, 4326)
        )
        RETURNING id INTO gentity_id;
    RETURN gentity_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION insert_into_garea(NEW ANYELEMENT, category_id INTEGER) RETURNS integer
AS $$
DECLARE gentity_id INTEGER;
BEGIN
    gentity_id = openhigis.insert_into_gentity(NEW);
    INSERT INTO enhydris_garea (gentity_ptr_id, category_id)
        VALUES (gentity_id, category_id);
    RETURN gentity_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION update_gentity(gentity_id INTEGER, OLD ANYELEMENT, NEW ANYELEMENT)
RETURNS void
AS $$
BEGIN
    UPDATE enhydris_gentity
        SET
            name=NEW.geographicalName,
            code=COALESCE(NEW.hydroId, ''),
            remarks=COALESCE(NEW.remarks, ''),
            geom=ST_Transform(NEW.geometry, 4326)
        WHERE id=gentity_id;
END;
$$ LANGUAGE plpgsql;

/* River basin districts */

DROP VIEW IF EXISTS RiverBasinDistrict;

CREATE VIEW RiverBasinDistrict
    AS SELECT
        rbd.imported_id AS id,
        g.name AS geographicalName,
        g.code AS hydroId,
        g.remarks,
        rbd.geom2100 AS geometry,
        ST_Perimeter(rbd.geom2100) / 1000 AS length_km,
        ST_Area(rbd.geom2100) / 1000000 AS area_sqkm
    FROM
        enhydris_gentity g
        INNER JOIN enhydris_openhigis_riverbasindistrict rbd
        ON rbd.garea_ptr_id = g.id;

CREATE OR REPLACE FUNCTION insert_into_RiverBasinDistrict() RETURNS TRIGGER
AS $$
DECLARE gentity_id INTEGER;
BEGIN
    gentity_id = openhigis.insert_into_garea(NEW, 2);
    INSERT INTO enhydris_openhigis_riverbasindistrict
        (garea_ptr_id, geom2100, imported_id)
        VALUES (gentity_id, NEW.geometry, NEW.id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER RiverBasinDistrict_insert
    INSTEAD OF INSERT ON RiverBasinDistrict
    FOR EACH ROW EXECUTE PROCEDURE insert_into_RiverBasinDistrict();

CREATE OR REPLACE FUNCTION update_RiverBasinDistrict() RETURNS TRIGGER
AS $$
DECLARE gentity_id INTEGER;
BEGIN
    SELECT garea_ptr_id INTO gentity_id FROM enhydris_openhigis_riverbasindistrict
        WHERE imported_id=OLD.id;
    PERFORM openhigis.update_gentity(gentity_id, OLD, NEW);
    UPDATE enhydris_openhigis_riverbasindistrict
    SET geom2100=NEW.geometry
    WHERE imported_id=OLD.id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER RiverBasinDistrict_update
    INSTEAD OF UPDATE ON RiverBasinDistrict
    FOR EACH ROW EXECUTE PROCEDURE update_RiverBasinDistrict();

CREATE OR REPLACE FUNCTION delete_RiverBasinDistrict()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE gentity_id INTEGER;
BEGIN
    SELECT garea_ptr_id INTO gentity_id FROM enhydris_openhigis_riverbasindistrict
        WHERE imported_id=OLD.id;
    DELETE FROM enhydris_openhigis_riverbasindistrict WHERE garea_ptr_id=gentity_id;
    DELETE FROM enhydris_garea WHERE gentity_ptr_id=gentity_id;
    DELETE FROM enhydris_gentity WHERE id=gentity_id;
    RETURN OLD;
END;
$$;

CREATE TRIGGER RiverBasinDistrict_delete
    INSTEAD OF DELETE ON RiverBasinDistrict
    FOR EACH ROW EXECUTE PROCEDURE delete_RiverBasinDistrict();

/* Drainage basins */

DROP VIEW IF EXISTS DrainageBasin;

CREATE VIEW DrainageBasin
    AS SELECT
        drb.imported_id as id,
        g.name AS geographicalName,
        g.code AS hydroId,
        g.last_modified AS beginLifespanVersion,
        g.remarks,
        drb.geom2100 AS geometry,
        riverbasin.imported_id AS riverBasin,
        CASE WHEN drb.man_made IS NULL THEN ''
             WHEN drb.man_made THEN 'manMade'
             ELSE 'natural'
             END AS origin,
        drb.hydro_order AS basinOrder,
        drb.hydro_order_scheme AS basinOrderScheme,
        drb.hydro_order_scope AS basinOrderScope,
        ST_Area(drb.geom2100) / 1000000 AS area,
        drb.total_area AS totalArea,
        drb.mean_slope AS meanSlope,
        drb.mean_elevation AS meanElevation
    FROM
        enhydris_gentity g
        INNER JOIN enhydris_openhigis_drainagebasin drb
            ON drb.garea_ptr_id = g.id
        INNER JOIN enhydris_openhigis_riverbasin riverbasin
            ON drb.river_basin_id = riverbasin.garea_ptr_id;

CREATE OR REPLACE FUNCTION insert_into_DrainageBasin() RETURNS TRIGGER
AS $$
DECLARE
    gentity_id INTEGER;
    new_river_basin_id INTEGER;
BEGIN
    gentity_id = openhigis.insert_into_garea(NEW, 4);
    SELECT garea_ptr_id INTO new_river_basin_id
        FROM enhydris_openhigis_riverbasin
        WHERE imported_id = NEW.riverBasin;
    INSERT INTO enhydris_openhigis_drainagebasin
        (garea_ptr_id, geom2100, river_basin_id, man_made, hydro_order,
        hydro_order_scheme, hydro_order_scope, total_area, mean_slope,
        mean_elevation, imported_id)
        VALUES (gentity_id, NEW.geometry, new_river_basin_id,
            NEW.origin = 'manMade', COALESCE(NEW.basinOrder, ''),
            COALESCE(NEW.basinOrderScheme, ''),
            COALESCE(NEW.basinOrderScope, ''), NEW.totalArea, NEW.meanSlope,
            NEW.meanElevation, NEW.id
        );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER DrainageBasin_insert
    INSTEAD OF INSERT ON DrainageBasin
    FOR EACH ROW EXECUTE PROCEDURE insert_into_DrainageBasin();

CREATE OR REPLACE FUNCTION update_DrainageBasin() RETURNS TRIGGER
AS $$
DECLARE
    gentity_id INTEGER;
    new_river_basin_id INTEGER;
BEGIN
    SELECT garea_ptr_id INTO gentity_id FROM enhydris_openhigis_drainagebasin
        WHERE imported_id=OLD.id;
    SELECT garea_ptr_id INTO new_river_basin_id
        FROM enhydris_openhigis_riverbasin
        WHERE imported_id = NEW.riverBasin;
    PERFORM openhigis.update_gentity(gentity_id, OLD, NEW);
    UPDATE enhydris_openhigis_drainagebasin
    SET
        geom2100=NEW.geometry,
        river_basin_id=new_river_basin_id,
        man_made=(NEW.origin = 'manMade'),
        hydro_order=COALESCE(NEW.basinOrder, ''),
        hydro_order_scheme=COALESCE(NEW.basinOrderScheme, ''),
        hydro_order_scope=COALESCE(NEW.basinOrderScope, ''),
        total_area=NEW.totalArea,
        mean_slope=NEW.meanSlope,
        mean_elevation=NEW.meanElevation
        WHERE imported_id=OLD.id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER DrainageBasin_update
    INSTEAD OF UPDATE ON DrainageBasin
    FOR EACH ROW EXECUTE PROCEDURE update_DrainageBasin();

CREATE OR REPLACE FUNCTION delete_DrainageBasin()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE gentity_id INTEGER;
BEGIN
    SELECT garea_ptr_id INTO gentity_id FROM enhydris_openhigis_drainagebasin
        WHERE imported_id=OLD.id;
    DELETE FROM enhydris_openhigis_drainagebasin WHERE garea_ptr_id=gentity_id;
    DELETE FROM enhydris_garea WHERE gentity_ptr_id=gentity_id;
    DELETE FROM enhydris_gentity WHERE id=gentity_id;
    RETURN OLD;
END;
$$;

CREATE TRIGGER DrainageBasin_delete
    INSTEAD OF DELETE ON DrainageBasin
    FOR EACH ROW EXECUTE PROCEDURE delete_DrainageBasin();

/* River basins */

DROP VIEW IF EXISTS RiverBasin;

CREATE VIEW RiverBasin
    AS SELECT
        rb.imported_id AS id,
        g.name AS geographicalName,
        g.code AS hydroId,
        g.last_modified AS beginLifespanVersion,
        g.remarks,
        rb.geom2100 AS geometry,
        CASE WHEN rb.man_made IS NULL THEN ''
             WHEN rb.man_made THEN 'manMade'
             ELSE 'natural'
             END AS origin,
        ST_Area(rb.geom2100) / 1000000 AS area,
        rb.mean_slope AS meanSlope,
        rb.mean_elevation AS meanElevation
    FROM
        enhydris_gentity g
        INNER JOIN enhydris_openhigis_riverbasin rb
        ON rb.garea_ptr_id = g.id;

CREATE OR REPLACE FUNCTION insert_into_RiverBasin() RETURNS TRIGGER
AS $$
DECLARE gentity_id INTEGER;
BEGIN
    gentity_id = openhigis.insert_into_garea(NEW, 3);
    INSERT INTO enhydris_openhigis_riverbasin
        (garea_ptr_id, geom2100, man_made, mean_slope, mean_elevation,
            imported_id)
        VALUES (gentity_id, NEW.geometry, NEW.origin = 'manMade',
            NEW.meanSlope, NEW.meanElevation, NEW.id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER RiverBasin_insert
    INSTEAD OF INSERT ON RiverBasin
    FOR EACH ROW EXECUTE PROCEDURE insert_into_RiverBasin();

CREATE OR REPLACE FUNCTION update_RiverBasin() RETURNS TRIGGER
AS $$
DECLARE gentity_id INTEGER;
BEGIN
    SELECT garea_ptr_id INTO gentity_id FROM enhydris_openhigis_riverbasin
        WHERE imported_id=OLD.id;
    PERFORM openhigis.update_gentity(gentity_id, OLD, NEW);
    UPDATE enhydris_openhigis_riverbasin
    SET
        geom2100=NEW.geometry,
        man_made=(NEW.origin = 'manMade'),
        mean_slope=NEW.meanSlope,
        mean_elevation=NEW.meanElevation
        WHERE imported_id=OLD.id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER RiverBasin_update
    INSTEAD OF UPDATE ON RiverBasin
    FOR EACH ROW EXECUTE PROCEDURE update_RiverBasin();

CREATE OR REPLACE FUNCTION delete_RiverBasin()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE gentity_id INTEGER;
BEGIN
    SELECT garea_ptr_id INTO gentity_id FROM enhydris_openhigis_riverbasin
        WHERE imported_id=OLD.id;
    DELETE FROM enhydris_openhigis_riverbasin WHERE garea_ptr_id=gentity_id;
    DELETE FROM enhydris_garea WHERE gentity_ptr_id=gentity_id;
    DELETE FROM enhydris_gentity WHERE id=gentity_id;
    RETURN OLD;
END;
$$;

CREATE TRIGGER RiverBasin_delete
    INSTEAD OF DELETE ON RiverBasin
    FOR EACH ROW EXECUTE PROCEDURE delete_RiverBasin();

/* Station basins */

DROP VIEW IF EXISTS StationBasin;

CREATE VIEW StationBasin
    AS SELECT
        station_id AS id,
        'Λεκάνη ανάντη του σταθμού ' || station.name AS geographicalName,
        g.code AS hydroId,
        g.last_modified AS beginLifespanVersion,
        g.remarks,
        sb.geom2100 AS geometry,
        riverbasin.imported_id AS riverBasin,
        CASE WHEN sb.man_made IS NULL THEN ''
             WHEN sb.man_made THEN 'manMade'
             ELSE 'natural'
             END AS origin,
        ST_Area(sb.geom2100) / 1000000 AS area,
        sb.mean_slope AS meanSlope,
        sb.mean_elevation AS meanElevation
    FROM
        enhydris_gentity g
        INNER JOIN enhydris_openhigis_stationbasin sb
        ON sb.garea_ptr_id = g.id
        INNER JOIN enhydris_openhigis_riverbasin riverbasin
        ON riverbasin.garea_ptr_id = sb.river_basin_id
        INNER JOIN enhydris_gentity station
        ON station.id = sb.station_id;

CREATE OR REPLACE FUNCTION insert_into_StationBasin() RETURNS TRIGGER
AS $$
DECLARE
    gentity_id INTEGER;
    new_river_basin_id INTEGER;
BEGIN
    gentity_id = openhigis.insert_into_garea(NEW, 5);
    SELECT garea_ptr_id INTO new_river_basin_id
        FROM enhydris_openhigis_riverbasin
        WHERE imported_id = NEW.riverBasin;
    INSERT INTO enhydris_openhigis_stationbasin
        (garea_ptr_id, geom2100, man_made, mean_slope, mean_elevation,
            river_basin_id, station_id)
        VALUES (gentity_id, NEW.geometry, NEW.origin = 'manMade',
            NEW.meanSlope, NEW.meanElevation, new_river_basin_id, NEW.id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER StationBasin_insert
    INSTEAD OF INSERT ON StationBasin
    FOR EACH ROW EXECUTE PROCEDURE insert_into_StationBasin();

CREATE OR REPLACE FUNCTION update_StationBasin() RETURNS TRIGGER
AS $$
DECLARE
    gentity_id INTEGER;
    new_river_basin_id INTEGER;
BEGIN
    SELECT garea_ptr_id INTO gentity_id FROM enhydris_openhigis_stationbasin
        WHERE station_id=OLD.id;
    SELECT garea_ptr_id INTO new_river_basin_id
        FROM enhydris_openhigis_riverbasin
        WHERE imported_id = NEW.riverBasin;
    PERFORM openhigis.update_gentity(gentity_id, OLD, NEW);
    UPDATE enhydris_openhigis_stationbasin
    SET
        geom2100=NEW.geometry,
        man_made=(NEW.origin = 'manMade'),
        mean_slope=NEW.meanSlope,
        mean_elevation=NEW.meanElevation,
        river_basin_id=new_river_basin_id
        WHERE station_id=OLD.id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER StationBasin_update
    INSTEAD OF UPDATE ON StationBasin
    FOR EACH ROW EXECUTE PROCEDURE update_StationBasin();

CREATE OR REPLACE FUNCTION delete_StationBasin()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE gentity_id INTEGER;
BEGIN
    SELECT garea_ptr_id INTO gentity_id FROM enhydris_openhigis_stationbasin
        WHERE station_id=OLD.id;
    DELETE FROM enhydris_openhigis_stationbasin WHERE garea_ptr_id=gentity_id;
    DELETE FROM enhydris_garea WHERE gentity_ptr_id=gentity_id;
    DELETE FROM enhydris_gentity WHERE id=gentity_id;
    RETURN OLD;
END;
$$;

CREATE TRIGGER StationBasin_delete
    INSTEAD OF DELETE ON StationBasin
    FOR EACH ROW EXECUTE PROCEDURE delete_StationBasin();

/* Give permissions */

GRANT USAGE ON SCHEMA openhigis TO mapserver, anton;
GRANT SELECT ON ALL TABLES IN SCHEMA openhigis TO mapserver;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA openhigis TO anton;
GRANT SELECT, INSERT, UPDATE, DELETE
    ON
    enhydris_openhigis_riverbasin,
    enhydris_openhigis_drainagebasin,
    enhydris_openhigis_riverbasindistrict,
    enhydris_openhigis_stationbasin,
    enhydris_openhigis_station,
    enhydris_garea,
    enhydris_gentity
    TO anton;

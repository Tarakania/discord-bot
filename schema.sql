-- TABLES --

/* Races
 * TODO
 */

/* Classes
 * TODO
 */

CREATE TABLE players (
    discord_id bigint PRIMARY KEY,
    nick       varchar(128) UNIQUE,
    race       smallint NOT NULL,
    class      smallint NOT NULL,
    xp         integer NOT NULL DEFAULT 0 CHECK (xp >= 0),
    money      integer NOT NULL DEFAULT 0 CHECK (money >= 0),
    inventory  integer[] NOT NULL DEFAULT ARRAY[]::integer[]
);

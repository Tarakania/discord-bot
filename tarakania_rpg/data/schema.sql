-- TABLES --

/* Races
 * see rpg/races.yaml
 */

/* locations
* see rpg/locations.yaml
*/

/* Classes
 * see rpg/classes.py
 */

CREATE TABLE players (
  discord_id bigint PRIMARY KEY,
  nick       varchar (128) UNIQUE NOT NULL,
  race       smallint NOT NULL,
  class      smallint NOT NULL,
  location   smallint NOT NULL,
  xp         integer NOT NULL DEFAULT 0 CHECK (xp >= 0),
  money      integer NOT NULL DEFAULT 0 CHECK (money >= 0),
  inventory  integer[] NOT NULL DEFAULT ARRAY[]::integer[]
);

CREATE TABLE equipment (
  discord_id bigint PRIMARY KEY REFERENCES players(discord_id) ON DELETE CASCADE,
  weapon     smallint,
  helmet     smallint,
  chestplate smallint,
  leggings   smallint,
  boots      smallint,
  shield     smallint
);

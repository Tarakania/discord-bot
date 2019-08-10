-- TABLES --

/* Races
 * 0: Терраконы
 * 1: Славоны
 * 2: Сутхоны
 * 3: Новсеноны
 * 4: Желтофрактилы
 * 5: Черноманы
 * 6: Нортамоны
 */

/* locations
* 0: Терраконы
* 1: Славоны
* 2: Сутхоны
* 3: Новсеноны
* 4: Желтофрактилы
* 5: Черноманы
* 6: Нортамоны
*/

/* Classes
 * 0: Воин
 * 1: Паладин
 * 2: Маг
 * 3: Разбойник
 * 4: Стрелок
 */

CREATE TABLE players (
    discord_id bigint PRIMARY KEY,
    nick       varchar(128) UNIQUE NOT NULL,
    race       smallint NOT NULL,
    class      smallint NOT NULL,
    location   smallint NOT NULL,
    xp         integer NOT NULL DEFAULT 0 CHECK (xp >= 0),
    money      integer NOT NULL DEFAULT 0 CHECK (money >= 0),
    inventory  integer[] NOT NULL DEFAULT ARRAY[]::integer[]
);

BEGIN;

-- bcrypt-Hashes sind derzeit 60 Zeichen lang. TEXT verhindert, dass ein Hash
-- durch eine zu kurze bestehende Spalte abgeschnitten wird.
ALTER TABLE users
    ALTER COLUMN password TYPE TEXT;

-- Der Index bricht bewusst ab, falls bereits Benutzernamen existieren, die
-- sich nur durch Gross-/Kleinschreibung unterscheiden. Diese Daten muessen
-- vor der Migration eindeutig bereinigt werden.
CREATE UNIQUE INDEX IF NOT EXISTS users_username_lower_unique
    ON users (lower(username));

COMMIT;

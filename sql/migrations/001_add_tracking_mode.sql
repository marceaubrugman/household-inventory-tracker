BEGIN;

ALTER TABLE hit.items
ADD COLUMN tracking_mode VARCHAR(20);

UPDATE hit.items
SET tracking_mode = 'quantity'
WHERE tracking_mode IS NULL;

ALTER TABLE hit.items
ALTER COLUMN tracking_mode SET DEFAULT 'quantity';

ALTER TABLE hit.items
ADD CONSTRAINT tracking_mode_allowed
CHECK (tracking_mode IN ('quantity', 'individual'));

ALTER TABLE hit.items
ALTER COLUMN tracking_mode SET NOT NULL;

COMMIT;

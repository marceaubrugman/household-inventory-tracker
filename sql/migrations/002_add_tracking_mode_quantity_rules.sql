BEGIN;

ALTER TABLE hit.items
ALTER COLUMN quantity DROP NOT NULL;

ALTER TABLE hit.items
ALTER COLUMN minimum_quantity DROP NOT NULL;

ALTER TABLE hit.items
ADD CONSTRAINT tracking_mode_quantity_fields
CHECK (
    (
        tracking_mode = 'quantity'
        AND quantity IS NOT NULL
        AND minimum_quantity IS NOT NULL
    )
    OR
    (
        tracking_mode = 'individual'
        AND quantity IS NULL
        AND minimum_quantity IS NULL
    )
);

COMMIT;

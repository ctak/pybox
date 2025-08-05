-- DELETE FROM ecas_db.atlas_ecas_raw;

        SELECT
            eqp_id,
            pm_mode,
            tm,
            ROW_NUMBER() OVER (PARTITION BY eqp_id ORDER BY tm DESC) as rn
        FROM
            atlas_ecas_raw
        WHERE pm_mode IS NOT NULL
        ;
        
 WITH RankedLogs AS (
        SELECT
            eqp_id,
            pm_mode,
            tm,
            ROW_NUMBER() OVER (PARTITION BY eqp_id ORDER BY tm DESC) as rn
        FROM
            atlas_ecas_raw
        WHERE pm_mode IS NOT NULL
    )
    SELECT
        eqp_id,
        pm_mode,
        tm,
        rn
    FROM
        RankedLogs
    WHERE
        rn = 1;
        
        
      SELECT
            eqp_id,
            pm_mode,
            tm,
            val
--             ROW_NUMBER() OVER (PARTITION BY eqp_id ORDER BY tm DESC) as rn
        FROM
            atlas_ecas_raw
         WHERE EQP_ID = 'EQP-017';
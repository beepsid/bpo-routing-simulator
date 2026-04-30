-- Weekly drop rate

SELECT 
    DATE_FORMAT(call_timestamp, '%Y-%u') AS week,
    (SUM(CASE 
        WHEN resolution_status = 'Dropped' THEN 1 
        ELSE 0 
    END) * 100.0) / COUNT(*) AS drop_rate
FROM call_center_logs
GROUP BY week
ORDER BY week;

-- Weekly drop rate for tech_support

SELECT 
    DATE_FORMAT(call_timestamp, '%Y-%u') AS week,
    (SUM(CASE 
        WHEN resolution_status = 'Dropped' THEN 1 
        ELSE 0 
    END) * 100.0) / COUNT(*) AS drop_rate
FROM call_center_logs
WHERE issue_category = 'Tech Support'
GROUP BY week
ORDER BY week;

-- Rolling average drop rate per week

SELECT 
    week,
    drop_rate,
    AVG(drop_rate) OVER (
        ORDER BY week 
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS rolling_avg
FROM (
    SELECT 
        DATE_FORMAT(call_timestamp, '%Y-%u') AS week,
        (SUM(CASE 
            WHEN resolution_status = 'Dropped' THEN 1 
            ELSE 0 
        END) * 100.0) / COUNT(*) AS drop_rate
    FROM call_center_logs
    WHERE issue_category = 'Tech Support'
    GROUP BY week
) t;
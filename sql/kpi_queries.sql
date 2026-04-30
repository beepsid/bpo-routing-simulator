-- Total Calls
SELECT COUNT(*) FROM call_center_logs;

-- Average Handling Time
SELECT AVG(call_duration_seconds) AS avg_aht FROM call_center_logs;

-- AHT by Category
SELECT issue_category, AVG(call_duration_seconds)
FROM call_center_logs
GROUP BY issue_category;

-- Drop Rate
SELECT 
(SUM(CASE WHEN resolution_status='Dropped' THEN 1 ELSE 0 END)*100.0)/COUNT(*) 
AS drop_rate_percent
FROM call_center_logs;

-- Drop Rate by Category
SELECT issue_category,
(SUM(CASE WHEN resolution_status='Dropped' THEN 1 ELSE 0 END)*100.0)/COUNT(*) 
FROM call_center_logs
GROUP BY issue_category;

--Longer Queue Wait Time
SELECT
    (SUM(CASE 
        WHEN queue_wait_time > 60 THEN 1 
        ELSE 0 
    END) * 100.0) / COUNT(*) AS long_queue_time_percent
FROM call_center_logs;

-- Avg Queue Wait Time
SELECT AVG(queue_wait_time) FROM call_center_logs;

-- Resolution Distribution %
SELECT resolution_status,
(COUNT(*) * 100.0) / (SELECT COUNT(*) FROM call_center_logs)
FROM call_center_logs
GROUP BY resolution_status;

-- Top 5 Agents
SELECT agent_id, COUNT(*) AS total_calls
FROM call_center_logs
GROUP BY agent_id
ORDER BY total_calls DESC
LIMIT 5;

-- Drop rate by Agent
SELECT 
    agent_id,
    (SUM(CASE 
        WHEN resolution_status = 'Dropped' THEN 1 
        ELSE 0 
    END) * 100.0) / COUNT(*) AS drop_rate_percent
FROM call_center_logs
GROUP BY agent_id
ORDER BY drop_rate_percent DESC;
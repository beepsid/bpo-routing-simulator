USE bpo_project;

-- 1. Total Call Volume
SELECT COUNT(*) AS total_calls
FROM call_center_logs;


-- 2. Average Handling Time (AHT) - Overall
SELECT ROUND(AVG(call_duration_seconds), 2) AS avg_aht_seconds
FROM call_center_logs;


-- 3. AHT by Category (JOIN to categories)
SELECT
    c.category_name,
    ROUND(AVG(l.call_duration_seconds), 2)  AS avg_aht_seconds,
    c.sla_target_seconds                     AS sla_target,
    CASE
        WHEN AVG(l.call_duration_seconds) <= c.sla_target_seconds THEN 'Within SLA'
        ELSE 'Breached SLA'
    END AS sla_status
FROM call_center_logs l
JOIN categories c ON l.issue_category = c.category_name
GROUP BY c.category_name, c.sla_target_seconds
ORDER BY avg_aht_seconds DESC;


-- 4. SLA Adherence Rate by Department
SELECT
    c.category_name,
    COUNT(*)                                                        AS total_calls,
    SUM(CASE WHEN l.call_duration_seconds <= c.sla_target_seconds THEN 1 ELSE 0 END)
                                                                    AS calls_within_sla,
    ROUND(
        SUM(CASE WHEN l.call_duration_seconds <= c.sla_target_seconds THEN 1 ELSE 0 END)
        * 100.0 / COUNT(*), 2
    )                                                               AS sla_adherence_pct
FROM call_center_logs l
JOIN categories c ON l.issue_category = c.category_name
GROUP BY c.category_name
ORDER BY sla_adherence_pct DESC;


-- 5. First Call Resolution (FCR) Rate - Overall
SELECT
    ROUND(SUM(fcr) * 100.0 / COUNT(*), 2) AS fcr_rate_pct
FROM call_center_logs;


-- 6. FCR Rate by Category vs Target (JOIN)
SELECT
    c.category_name,
    ROUND(SUM(l.fcr) * 100.0 / COUNT(*), 2)    AS actual_fcr_pct,
    ROUND(c.target_fcr_rate * 100, 2)           AS target_fcr_pct,
    CASE
        WHEN SUM(l.fcr) * 1.0 / COUNT(*) >= c.target_fcr_rate THEN 'Met'
        ELSE 'Not Met'
    END AS fcr_target_status
FROM call_center_logs l
JOIN categories c ON l.issue_category = c.category_name
GROUP BY c.category_name, c.target_fcr_rate
ORDER BY actual_fcr_pct DESC;


-- 7. Drop Rate - Overall
SELECT
    ROUND(
        SUM(CASE WHEN resolution_status = 'Dropped' THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
    2) AS drop_rate_pct
FROM call_center_logs;


-- 8. Drop Rate by Category
SELECT
    issue_category,
    ROUND(
        SUM(CASE WHEN resolution_status = 'Dropped' THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
    2) AS drop_rate_pct
FROM call_center_logs
GROUP BY issue_category
ORDER BY drop_rate_pct DESC;


-- 9. Resolution Status Distribution %
SELECT
    resolution_status,
    COUNT(*)                                            AS total,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS pct
FROM call_center_logs
GROUP BY resolution_status;


-- 10. Agent Utilization - Calls Handled & Total Talk Time
--     (JOIN to agents for name and seniority)
SELECT
    a.agent_id,
    a.agent_name,
    a.seniority,
    a.department,
    COUNT(l.call_id)                                    AS total_calls,
    ROUND(SUM(l.call_duration_seconds) / 3600.0, 2)    AS total_talk_hours,
    ROUND(AVG(l.call_duration_seconds), 2)              AS avg_aht_seconds
FROM agents a
JOIN call_center_logs l ON a.agent_id = l.agent_id
GROUP BY a.agent_id, a.agent_name, a.seniority, a.department
ORDER BY total_calls DESC;


-- 11. Top 10 Agents by Call Volume
SELECT
    a.agent_id,
    a.agent_name,
    a.department,
    COUNT(l.call_id) AS total_calls
FROM agents a
JOIN call_center_logs l ON a.agent_id = l.agent_id
GROUP BY a.agent_id, a.agent_name, a.department
ORDER BY total_calls DESC
LIMIT 10;


-- 12. Agent Performance Ranking by FCR Rate
--     (window function: RANK)
SELECT
    agent_id,
    total_calls,
    fcr_rate_pct,
    RANK() OVER (ORDER BY fcr_rate_pct DESC) AS fcr_rank
FROM (
    SELECT
        agent_id,
        COUNT(*)                                        AS total_calls,
        ROUND(SUM(fcr) * 100.0 / COUNT(*), 2)          AS fcr_rate_pct
    FROM call_center_logs
    GROUP BY agent_id
    HAVING COUNT(*) >= 50
) ranked_agents;


-- 13. Drop Rate by Agent with Ranking
--     (window function: RANK)
SELECT
    a.agent_id,
    a.agent_name,
    a.seniority,
    agent_stats.total_calls,
    agent_stats.drop_rate_pct,
    RANK() OVER (ORDER BY agent_stats.drop_rate_pct DESC) AS drop_rank
FROM (
    SELECT
        agent_id,
        COUNT(*)                                                                AS total_calls,
        ROUND(
            SUM(CASE WHEN resolution_status = 'Dropped' THEN 1 ELSE 0 END)
            * 100.0 / COUNT(*), 2
        )                                                                       AS drop_rate_pct
    FROM call_center_logs
    GROUP BY agent_id
) agent_stats
JOIN agents a ON agent_stats.agent_id = a.agent_id
ORDER BY drop_rate_pct DESC;


-- 14. Queue Wait Time Analysis
SELECT
    ROUND(AVG(queue_wait_time), 2)                                          AS avg_wait_seconds,
    MAX(queue_wait_time)                                                     AS max_wait_seconds,
    ROUND(
        SUM(CASE WHEN queue_wait_time > 60 THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
    2)                                                                       AS pct_over_60s
FROM call_center_logs;


-- 15. Queue Wait Time by Category (JOIN)
SELECT
    c.category_name,
    ROUND(AVG(l.queue_wait_time), 2)    AS avg_wait_seconds,
    MAX(l.queue_wait_time)              AS max_wait_seconds,
    ROUND(
        SUM(CASE WHEN l.queue_wait_time > 60 THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
    2)                                  AS pct_over_60s
FROM call_center_logs l
JOIN categories c ON l.issue_category = c.category_name
GROUP BY c.category_name
ORDER BY avg_wait_seconds DESC;


-- 16. Monthly Call Volume Trend
--     (window function: running total)
SELECT
    month,
    monthly_calls,
    SUM(monthly_calls) OVER (ORDER BY month) AS running_total
FROM (
    SELECT
        DATE_FORMAT(call_timestamp, '%Y-%m') AS month,
        COUNT(*)                             AS monthly_calls
    FROM call_center_logs
    GROUP BY month
) monthly;


-- 17. Agent Performance vs Department Average
--     (subquery comparison)
SELECT
    a.agent_id,
    a.agent_name,
    a.department,
    ROUND(AVG(l.call_duration_seconds), 2)  AS agent_aht,
    dept_avg.dept_avg_aht,
    ROUND(AVG(l.call_duration_seconds) - dept_avg.dept_avg_aht, 2) AS diff_from_dept_avg
FROM call_center_logs l
JOIN agents a ON l.agent_id = a.agent_id
JOIN (
    SELECT
        a2.department,
        ROUND(AVG(l2.call_duration_seconds), 2) AS dept_avg_aht
    FROM call_center_logs l2
    JOIN agents a2 ON l2.agent_id = a2.agent_id
    GROUP BY a2.department
) dept_avg ON a.department = dept_avg.department
GROUP BY a.agent_id, a.agent_name, a.department, dept_avg.dept_avg_aht
ORDER BY diff_from_dept_avg DESC;

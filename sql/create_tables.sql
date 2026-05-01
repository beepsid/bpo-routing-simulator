CREATE DATABASE IF NOT EXISTS bpo_project;
USE bpo_project;

-- Category reference table
CREATE TABLE IF NOT EXISTS categories (
    category_id     CHAR(6)      PRIMARY KEY,
    category_name   VARCHAR(20)  NOT NULL UNIQUE,
    sla_target_seconds INT       NOT NULL,
    target_fcr_rate DECIMAL(4,2) NOT NULL
);

-- Agent reference table
CREATE TABLE IF NOT EXISTS agents (
    agent_id    CHAR(4)     PRIMARY KEY,
    agent_name  VARCHAR(100) NOT NULL,
    department  VARCHAR(20),
    seniority   VARCHAR(10),
    hire_date   DATE
);

-- Main call log table
CREATE TABLE IF NOT EXISTS call_center_logs (
    call_id                CHAR(7)     PRIMARY KEY,
    call_timestamp         DATETIME    NOT NULL,
    agent_id               CHAR(4)     NOT NULL,
    issue_category         VARCHAR(20),
    call_duration_seconds  INT,
    queue_wait_time        INT,
    resolution_status      VARCHAR(20),
    fcr                    TINYINT(1)  DEFAULT 0,
    FOREIGN KEY (agent_id)       REFERENCES agents(agent_id),
    FOREIGN KEY (issue_category) REFERENCES categories(category_name)
);

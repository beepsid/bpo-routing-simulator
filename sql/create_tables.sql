CREATE DATABASE bpo_project;
USE bpo_project;

CREATE TABLE call_center_logs (
    call_id CHAR(7) PRIMARY KEY,
    call_timestamp DATETIME NOT NULL,
    agent_id CHAR(4) NOT NULL,
    issue_category VARCHAR(20),
    call_duration_seconds INT,
    queue_wait_time INT,
    resolution_status VARCHAR(20)
);
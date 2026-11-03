DROP DATABASE IF EXISTS sms;
CREATE DATABASE sms CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE sms;

CREATE TABLE student (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name  VARCHAR(100) NOT NULL,
    email      VARCHAR(150) NOT NULL UNIQUE,
    class_name VARCHAR(10)  NOT NULL
) ENGINE=InnoDB;

INSERT INTO student (first_name, last_name, email, class_name) VALUES
    ('Amir',  'Hassan', 'amir@school.no',  '2A'),
    ('Emma',  'Berg',   'emma@school.no',  '2A'),
    ('Jonas', 'Lie',    'jonas@school.no', '2B'),
    ('Sara',  'Khan',   'sara@school.no',  '2B'),
    ('Nora',  'Haugen', 'nora@school.no',  '2A'),
    ('Ali',   'Dahl',   'ali@school.no',   '2B');
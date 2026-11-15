-- Lecture 5, Step 1.2: who may do what. Run it in DataGrip as root, AFTER courses.sql.
-- CRUD = INSERT, SELECT, UPDATE, DELETE. Each user gets only the letters it needs.
-- These are practice passwords for class. Real passwords never go on GitHub!
-- '%' means "from any computer": needed because MySQL runs in Docker.

CREATE USER IF NOT EXISTS 'sms_office'@'%'  IDENTIFIED BY 'office-pw-123';
CREATE USER IF NOT EXISTS 'sms_teacher'@'%' IDENTIFIED BY 'teacher-pw-123';
CREATE USER IF NOT EXISTS 'sms_report'@'%'  IDENTIFIED BY 'report-pw-123';

-- The school office: all four letters, on every table in sms
GRANT SELECT, INSERT, UPDATE, DELETE ON sms.* TO 'sms_office'@'%';

-- Teachers: read everything ...
GRANT SELECT ON sms.* TO 'sms_teacher'@'%';
-- ... sign students up for a course and take them off it (C and D on enrollment) ...
GRANT INSERT, DELETE ON sms.enrollment TO 'sms_teacher'@'%';
-- ... and change a course, for example more seats (U on course)
GRANT UPDATE ON sms.course TO 'sms_teacher'@'%';

-- The hallway screen and the principal's report: R only
GRANT SELECT ON sms.* TO 'sms_report'@'%';

-- Check: who has which letters?
SHOW GRANTS FOR 'sms_office'@'%';
SHOW GRANTS FOR 'sms_teacher'@'%';
SHOW GRANTS FOR 'sms_report'@'%';
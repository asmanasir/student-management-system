-- Lecture 5: the course tables. Run it in DataGrip as root, in the sms database.
-- IF NOT EXISTS / INSERT IGNORE: safe to run again, and it keeps tables you already have from week 2.
USE sms;

CREATE TABLE IF NOT EXISTS course (
    course_id    INT AUTO_INCREMENT PRIMARY KEY,
    course_code  VARCHAR(10)  NOT NULL UNIQUE,                 -- DB101: what people use, and what the address uses
    course_name  VARCHAR(100) NOT NULL,
    teacher      VARCHAR(50)  NOT NULL,
    max_students INT          NOT NULL CHECK (max_students BETWEEN 1 AND 200)
);

CREATE TABLE IF NOT EXISTS enrollment (
    student_id  INT  NOT NULL,
    course_id   INT  NOT NULL,
    enrolled_on DATE NOT NULL,
    PRIMARY KEY (student_id, course_id),                          -- a student takes a course only once
    FOREIGN KEY (student_id) REFERENCES student (student_id) ON DELETE CASCADE,   -- delete a student: the enrollments go too
    FOREIGN KEY (course_id)  REFERENCES course (course_id)                         -- delete a course: refused while it has students
);

INSERT IGNORE INTO course (course_code, course_name, teacher, max_students) VALUES
    ('DB101',  'Databases',       'Hansen', 30),
    ('PRG101', 'Programming',     'Lie',    25),
    ('WEB101', 'Web development', 'Hansen', 3);

INSERT IGNORE INTO enrollment (student_id, course_id, enrolled_on)
SELECT s.student_id, c.course_id, '2026-08-20'
FROM student s JOIN course c
  ON (s.email, c.course_code) IN (('amir@school.no', 'DB101'), ('emma@school.no', 'DB101'), ('emma@school.no', 'WEB101'),
                                  ('jonas@school.no', 'PRG101'), ('sara@school.no', 'WEB101'), ('ali@school.no', 'WEB101'));

GRANT SELECT, INSERT, UPDATE, DELETE ON sms.* TO 'sms_app'@'%';
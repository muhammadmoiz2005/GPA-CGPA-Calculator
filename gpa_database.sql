create database gpa;
use gpa;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    name TEXT NOT NULL,
    timestamp TEXT NOT NULL
);

-- Table: gpa_records
CREATE TABLE IF NOT EXISTS gpa_records (
    id INTEGER PRIMARY KEY auto_increment,
    user_name TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    course_name TEXT NOT NULL,
    total_marks REAL NOT NULL,
    obtained_marks REAL NOT NULL,
    credit_hours REAL NOT NULL,
    percentage REAL NOT NULL,
    grade TEXT NOT NULL,
    gpa REAL NOT NULL,
    grade_points REAL NOT NULL
);

select*from cgpa_records;

-- Table: cgpa_records
CREATE TABLE IF NOT EXISTS cgpa_records (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    user_name TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    semester_number INTEGER NOT NULL,
    semester_gpa REAL NOT NULL,
    credit_hours REAL NOT NULL,
    grade_points REAL NOT NULL
);

-- Table: calculation_summary
CREATE TABLE IF NOT EXISTS calculation_summary (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    user_name TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    calculation_type TEXT NOT NULL,
    final_result REAL NOT NULL,
    total_credit_hours REAL NOT NULL,
    total_grade_points REAL NOT NULL
);

-- ========================================
-- DATA ENTRIES START BELOW
-- ========================================


-- GPA Calculation Entry: 2025-11-30 23:06:56
-- User: Moiz
-- ==========================================

INSERT INTO users (name, timestamp)
VALUES ('Moiz', '2025-11-30 23:06:56');

INSERT INTO gpa_records (user_name, timestamp, course_name, total_marks, obtained_marks, credit_hours, percentage, grade, gpa, grade_points)
VALUES ('Moiz', '2025-11-30 23:06:56', 'AI', 100.0, 77.0, 2.0, 77.0, 'B+', 3.33, 6.66);
INSERT INTO gpa_records (user_name, timestamp, course_name, total_marks, obtained_marks, credit_hours, percentage, grade, gpa, grade_points)
VALUES ('Moiz', '2025-11-30 23:06:56', 'AI Lab', 100.0, 76.0, 1.0, 76.0, 'B+', 3.33, 3.33);
INSERT INTO gpa_records (user_name, timestamp, course_name, total_marks, obtained_marks, credit_hours, percentage, grade, gpa, grade_points)
VALUES ('Moiz', '2025-11-30 23:06:56', 'DS', 100.0, 80.0, 3.0, 80.0, 'A-', 3.66, 10.98);
INSERT INTO gpa_records (user_name, timestamp, course_name, total_marks, obtained_marks, credit_hours, percentage, grade, gpa, grade_points)
VALUES ('Moiz', '2025-11-30 23:06:56', 'DS Lab', 100.0, 92.0, 1.0, 92.0, 'A', 4.0, 4.0);
INSERT INTO gpa_records (user_name, timestamp, course_name, total_marks, obtained_marks, credit_hours, percentage, grade, gpa, grade_points)
VALUES ('Moiz', '2025-11-30 23:06:56', 'IS', 100.0, 75.0, 2.0, 75.0, 'B+', 3.33, 6.66);
INSERT INTO gpa_records (user_name, timestamp, course_name, total_marks, obtained_marks, credit_hours, percentage, grade, gpa, grade_points)
VALUES ('Moiz', '2025-11-30 23:06:56', 'IS Lab', 100.0, 78.0, 1.0, 78.0, 'B+', 3.33, 3.33);
INSERT INTO gpa_records (user_name, timestamp, course_name, total_marks, obtained_marks, credit_hours, percentage, grade, gpa, grade_points)
VALUES ('Moiz', '2025-11-30 23:06:56', 'CN', 100.0, 70.0, 2.0, 70.0, 'B-', 2.66, 5.32);
INSERT INTO gpa_records (user_name, timestamp, course_name, total_marks, obtained_marks, credit_hours, percentage, grade, gpa, grade_points)
VALUES ('Moiz', '2025-11-30 23:06:56', 'CN Lab ', 100.0, 80.0, 1.0, 80.0, 'A-', 3.66, 3.66);
INSERT INTO gpa_records (user_name, timestamp, course_name, total_marks, obtained_marks, credit_hours, percentage, grade, gpa, grade_points)
VALUES ('Moiz', '2025-11-30 23:06:56', 'P & S', 100.0, 91.0, 2.0, 91.0, 'A', 4.0, 8.0);
INSERT INTO gpa_records (user_name, timestamp, course_name, total_marks, obtained_marks, credit_hours, percentage, grade, gpa, grade_points)
VALUES ('Moiz', '2025-11-30 23:06:56', 'SE', 100.0, 75.0, 3.0, 75.0, 'B+', 3.33, 9.99);

INSERT INTO calculation_summary (user_name, timestamp, calculation_type, final_result, total_credit_hours, total_grade_points)
VALUES ('Moiz', '2025-11-30 23:06:56', 'GPA', 3.4405555555555556, 18.0, 61.93);


-- CGPA Calculation Entry: 2025-11-30 23:09:32
-- User: Moiz
-- ==========================================

INSERT INTO users (name, timestamp)
VALUES ('Moiz', '2025-11-30 23:09:32');

INSERT INTO cgpa_records (user_name, timestamp, semester_number, semester_gpa, credit_hours, grade_points)
VALUES ('Moiz', '2025-11-30 23:09:32', 1, 2.88, 17.0, 48.96);
INSERT INTO cgpa_records (user_name, timestamp, semester_number, semester_gpa, credit_hours, grade_points)
VALUES ('Moiz', '2025-11-30 23:09:32', 2, 3.53, 17.0, 60.01);
INSERT INTO cgpa_records (user_name, timestamp, semester_number, semester_gpa, credit_hours, grade_points)
VALUES ('Moiz', '2025-11-30 23:09:32', 3, 3.49, 17.0, 59.33);

INSERT INTO calculation_summary (user_name, timestamp, calculation_type, final_result, total_credit_hours, total_grade_points)
VALUES ('Moiz', '2025-11-30 23:09:32', 'CGPA', 3.3000000000000003, 51.0, 168.3);


-- GPA Calculation Entry: 2025-12-01 00:24:09
-- User: 
-- ==========================================

INSERT INTO users (name, timestamp)
VALUES ('', '2025-12-01 00:24:09');

INSERT INTO gpa_records (user_name, timestamp, course_name, total_marks, obtained_marks, credit_hours, percentage, grade, gpa, grade_points)
VALUES ('', '2025-12-01 00:24:09', 'Course 1', 100.0, 0.0, 3.0, 0.0, 'F', 0.0, 0.0);

INSERT INTO calculation_summary (user_name, timestamp, calculation_type, final_result, total_credit_hours, total_grade_points)
VALUES ('', '2025-12-01 00:24:09', 'GPA', 0.0, 3.0, 0.0);


-- GPA Calculation Entry: 2025-12-01 00:25:08
-- User: ALI
-- ==========================================

INSERT INTO users (name, timestamp)
VALUES ('ALI', '2025-12-01 00:25:08');

INSERT INTO gpa_records (user_name, timestamp, course_name, total_marks, obtained_marks, credit_hours, percentage, grade, gpa, grade_points)
VALUES ('ALI', '2025-12-01 00:25:08', 'Course 1', 100.0, 0.0, 3.0, 0.0, 'F', 0.0, 0.0);

INSERT INTO calculation_summary (user_name, timestamp, calculation_type, final_result, total_credit_hours, total_grade_points)
VALUES ('ALI', '2025-12-01 00:25:08', 'GPA', 0.0, 3.0, 0.0);


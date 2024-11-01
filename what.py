import psycopg2

### Generate advisor list
def gen_advisor_list():
    # List the ID and name of every student along with the name of the student's advisor
    query = '''
    SELECT student.ID, student.name, instructor.name AS advisor
    FROM student
    LEFT JOIN advisor ON(advisor.s_ID = student.ID)
    LEFT JOIN instructor ON(advisor.i_ID = instructor.ID)
    ;'''
    conn = psycopg2.connect(dbname="what")
    cur = conn.cursor()

    cur.execute(query)

    # Print results
    for student in cur:
        print(student[1]) # Student name
        print(f'\tStudent ID: {student[0]}')
        print(f'\tAdvisor: {student[2]}')
    
    conn.close()
    return


### Hire new instructor
def hire_instructor():
    
    # Connect to database
    conn = psycopg2.connect(dbname="what")
    cur = conn.cursor()
        
    
    def prompts():
        fac = input("Enter the name of a new faculty member: ")
        fid = input("Enter a new ID for the faculty member: ")
        dep = input("Enter the faculty member's department: ")
        sal = input("Enter the faculty member's salary: ")
        return fac,fid,dep,sal

    fac,fid,dep,sal = prompts()

    try:
        query = '''
        INSERT INTO instructor VALUES (%s,%s,%s,%s)
        ;'''
        cur.execute(query, (fid,fac,dep,sal)) # id, name, dept_name, salary
        conn.commit()
    except psycopg2.errors.UniqueViolation:
        print("ID already in use.")
        conn.rollback()
    except psycopg2.errors.ForeignKeyViolation:
        print("No such department.")
        conn.rollback()
    except psycopg2.errors.CheckViolation:
        print("Salary is too low.")
        conn.rollback()
    except psycopg2.Error as e:
        print("Other Error")
        print(e)
        conn.rollback()

    # query = "SELECT * FROM instructor;"
    # try:
    #     cur.execute(query)
    #     for instructor in cur:
    #         print(instructor[0], instructor[1], instructor[2], instructor[3])
    # except psycopg2.Error as e:
    #     print("Other Error")
    #     print(e)
    #     conn.rollback()
    # finally:
    #     conn.close()
    return


### Generate transcript
def gen_transcript():
    #  Prompt for a student ID and present a summary of that
    # student's information followed by a list of every class taken by that student. Classes
    # should be grouped by and in order of semester. For each class, the transcript should
    # display the course ID, section number, course name, credits, and grade. In each
    # semester group, display the GPA for that semester. At the end, display the current
    # cumulative GPA. For example, the transcript for Zhang might appear as follows.
    # Formatting details are at your discretion. Impress us.
    
    # Connect to database
    conn = psycopg2.connect(dbname="what")
    cur = conn.cursor()
        
    student_id = input("Enter a student ID: ")

    # Student name and department
    query = '''
    SELECT name, dept_name
    FROM student
    WHERE id LIKE %s
    ;'''
    cur.execute(query, (student_id,))
    name, dept_name = cur.fetchone()

    print(f'Student ID: {student_id}')
    print(f'{name}, {dept_name}')

    # Student courses and GPAs
    query = '''
    SELECT ID, name, student.dept_name, course_id, sec_id, semester, year, title, credits, grade
    FROM student
    JOIN takes USING (id)
    JOIN course USING (course_id)
    WHERE ID LIKE %s
    ORDER BY 
    year,
    case semester
        when 'Fall' then 3
        when 'Summer' then 2
        when 'Spring' then 1
        else 4
    end
    ;'''
    cur.execute(query, (student_id,))
    
    rows = cur.fetchall()

    current_semester = rows[0][5]
    current_year = rows[0][6]
    semester_grades = []
    all_grades = []
    semester_classes = []
    
    # Iterate each course
    for _, _, _, course_id, sec_id, semester, year, title, credits, grade in rows:
        # If new semester reached, print previous semester info
        if current_semester != semester:
            print_semester(current_semester, current_year, semester_classes, semester_grades)

            # Start new semester grades list
            semester_grades = []
            semester_classes = []
            current_semester = semester
            current_year = year
            
        # Collect courses
        if grade is None: g = 'N/A'
        else: g = grade
        semester_classes.append(f'{course_id} {sec_id} {title} ({credits}) {g}')

        all_grades.append((grade, credits))
        semester_grades.append((grade, credits)) # For current semester

    # Print last semester
    print_semester(current_semester, current_year, semester_classes, semester_grades)

    print(f'Cumulative GPA: {calculate_GPA(all_grades)}')
    return

def print_semester(current_semester, current_year, semester_classes, semester_grades):
    #Print Year, Semester, and GPA
    print(f'{current_semester} {current_year}')
    print(f'GPA: {calculate_GPA(semester_grades)}') # Semester GPA

    #Print the Semester's Courses
    for course in semester_classes:
        print(f'\t{course}')
    return

def calculate_GPA(grade_list):
    quality_points = 0
    total_credit_hours = 0

    for grade in grade_list:
        if not grade[0] is None:
            quality_points += (get_numeric_grade(grade[0]) * int(grade[1]))
            total_credit_hours += int(grade[1])

    if total_credit_hours == 0:
        return 'N/A'
    else:
        return round((quality_points / total_credit_hours), 2)

def get_numeric_grade(letter_grade):
    if letter_grade == 'A':
        return 4.0
    elif letter_grade == 'A-':
        return 3.7
    elif letter_grade == 'B+':
        return 3.3
    elif letter_grade == 'B':
        return 3.0
    elif letter_grade == 'B-':
        return 2.7
    elif letter_grade == 'C+':
        return 2.3
    elif letter_grade == 'C':
        return 2.0
    elif letter_grade == 'C-':
        return 1.7
    elif letter_grade == 'D+':
        return 1.3
    elif letter_grade == 'D':
        return 1.0
    elif letter_grade == 'D-':
        return 0.7
    elif letter_grade == 'F':
        return 0.0
    else:
        print(f'improper use: {str(letter_grade)}')
        return 0.0

### Generate course list
def gen_course_list():

    # Connect to database
    conn = psycopg2.connect(dbname="what")
    cur = conn.cursor()
        
    sem = input("Enter the semester: ")
    year = input("Enter the year: ")
    
    query = '''
    WITH enroll AS (
        SELECT course_id, sec_id, semester, year, COUNT(id) as enrollment
        FROM takes
        GROUP BY course_id, sec_id, semester, year
    )

    SELECT course_id, sec_id, title, credits, classroom.building, room_number, capacity, enrollment, day, start_hr, start_min, end_hr, end_min
    FROM course
    JOIN section USING(course_id)
    JOIN classroom USING(building, room_number)
    JOIN enroll USING(course_id, sec_id, semester, year)
    RIGHT JOIN time_slot USING(time_slot_id)
    WHERE semester = %s AND year = %s
    ORDER BY course_id ASC
    ;'''
    cur.execute(query, (sem, year))

    # Print results
    # Iterate through all courses
    is_first = True
    cur_course = ()
    
    
    for course_id, sec_id, title, credits, building, room_number, capacity, enrollment, day, start_hr, start_min, end_hr, end_min in cur:
        if is_first:
            is_first = False
        elif cur_course == (course_id, sec_id):
            print(f'\t\t{day} {start_hr}:{str(start_min).ljust(2, "0")} - {end_hr}:{str(end_min).ljust(2, "0")}')
            cur_course = (course_id, sec_id)
            continue
        cur_course = (course_id, sec_id)
        
        print(f'{course_id} {sec_id}: {title}')
        print(f'\tCredits: {credits}')
        print(f'\tLocation: {building} {room_number}')
        print(f'\tEnrollment: {enrollment} / {capacity}')
        print(f'\tMeet Times: \n\t\t{day} {start_hr}:{str(start_min).ljust(2, "0")} - {end_hr}:{str(end_min).ljust(2, "0")}')
    
    conn.close()
    return


### Register a student for a course
def register_student():

    # Connect to database
    conn = psycopg2.connect(dbname="what")
    cur = conn.cursor()
    
    student_id = input("Enter the student ID: ")
    course_id = input("Enter the course ID: ")
    section_id = input("Enter the section ID: ")
    sem = input("Enter the semester: ")
    year = input("Enter the year: ")

    query = '''
    INSERT INTO takes VALUES (%s, %s, %s, %s, %s)
    ;'''

    try:
        cur.execute(query, (student_id, course_id, section_id, sem, year))
        conn.commit()
    except psycopg2.errors.ForeignKeyViolation:
        print("No such ID.")
        print(e)
        conn.rollback()
    except psycopg2.errors.DataException:
        print("Improper value.")
        print(e)
        conn.rollback()
    except psycopg2.Error as e:
        print("Other Error")
        print(e)
        conn.rollback()
    finally:
        conn.close

### Menu



# Get user input
terminated = False
quit_command_list = ("quit", "q", "Quit", "QUIT", "Q", "exit", "Exit", "EXIT")

while (not terminated):
    # List all possible actions
    print("What action would you like to take?")
    print("\t--Input 1 to generate a list of all advisors")
    print("\t--Input 2 to hire a new instructor")
    print("\t--Input 3 to generate a student's transcript")
    print("\t--Input 4 to generate the course list")
    print("\t--Input 5 to register a student for a course")
    action = input("Please input a number to indicate your selection: ")
    action = action.strip()

    if action == '1':
        gen_advisor_list()
    elif action == '2':
        hire_instructor()
    elif action == '3':
        gen_transcript()
    elif action == '4':
        gen_course_list()
    elif action == '5':
        register_student()
    elif action in quit_command_list:
        terminated = True
    else:
        print("Invalid selection. Please enter a single integer from 1 to 5.")
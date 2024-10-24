import psycopg2

### Generate advisor list
def gen_advisor_list():
    # List the ID and name of every student along with the name of the student's advisor
    query = '''
    SELECT student.ID, student.name, instructor.name AS advisor
    FROM student
    LEFT JOIN advisor ON(advisor.s_ID = student.ID)
    JOIN instructor ON(advisor.i_ID = instructor.ID)
    ;'''
    conn = psycopg2.connect(dbname="what")
    cur = conn.cursor()

    cur.execute(query)
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

    query = "select * from instructor"
    try:
        cur.execute(query)
        for instructor in cur:
            print(instructor[0], instructor[1], instructor[2], instructor[3])
    except psycopg2.Error as e:
        print("Other Error")
        print(e)
        conn.rollback()
    finally:
        conn.close()

### Generate transcript
def gen_transcript():
    
    # Connect to database
    conn = psycopg2.connect(dbname="what")
    cur = conn.cursor()
        
    student_id = input("Enter a student ID: ")

    query = '''
    SELECT ID, name, dept_name
    FROM student, 
    ;'''

### Generate course list
def gen_course_list():

    # Connect to database
    conn = psycopg2.connect(dbname="what")
    cur = conn.cursor()
        
    sem = input("Enter the semester: ")
    year = input("Enter the year: ")
    
    query = '''
    WITH enroll AS (
        SELECT course_id, COUNT(id) as enrollment
        FROM takes
        GROUP BY course_id
    )

    SELECT course_id, sec_id, title, credits, building, room_number, capacity, enrollment, day, start_hr, start_min, end_hr, end_min
    FROM course
    JOIN section USING(course_id)
    JOIN classroom USING(room_number)
    JOIN enroll USING(course_id)
    JOIN time_slot USING(time_slot_id)
    WHERE semester LIKE :sem AND year LIKE :year
    ORDER BY course_id ASC
    ;'''

### Register a student for a course
def register_student():

    # Connect to database
    conn = psycopg2.connect(dbname="what")
    cur = conn.cursor()
    
    sem = input("Enter the semester: ")
    year = input("Enter the year: ")
    student_id = input("Enter the student ID: ")
    course_id = input("Enter the course ID: ")
    section_id = input("Enter the section ID: ")

    query = '''
    INSERT INTO TAKES VALUES (%s, %s, %s, %s, %s)
    ;'''

    try:
        cur.execute(query, (sem,year,student_id,course_id, section_id))
        conn.commit()
    except psycopg2.errors.ForeignKeyViolation:
        print("No such ID.")
        conn.rollback()
    finally:
        conn.close

### Menu

# List all possible actions
print("What action would you like to take?")
print("\t--Input 1 to generate a list of all advisors")
print("\t--Input 2 to hire a new instructor")
print("\t--Input 3 to generate a student's transcript")
print("\t--Input 4 to generate the course list")
print("\t--Input 5 to register a student for a course")

# Get user input
terminated = False
quit_command_list = ("quit", "q", "Quit", "QUIT", "Q", "exit", "Exit", "EXIT")

while (not terminated):
    action = input("Please input a number to indicate your selection: ")

    if action == 1:
        gen_advisor_list()
    elif action == 2:
        hire_instructor()
    elif action == 3:
        gen_transcript()
    elif action == 4:
        gen_course_list()
    elif action == 5:
        register_student()
    elif quit_command_list.contains(action):
        terminated = True
    else:
        print("Invalid selection. Please enter a single integer from 1 to 5.")
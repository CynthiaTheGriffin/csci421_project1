import psycopg2


### Menu

# List all possible actions
print("What action would you like to take?")
print("\t--Input 1 to generate a list of all advisors")
print("\t--Input 2 to hire a new instructor")
print("\t--Input 3 to generate a student's transcript")
print("\t--Input 4 to generate the course list")
print("\t--Input 5 to register a student for a course")

# Get user input
action = input("Please input a number to indicate your selection: ")

# Connect to database
conn = psycopg2.connect(dbname="what")
cur = conn.cursor()


### Generate advisor list
def gen_advisor_list():
    query = ''
    cur.execute(query)
    pass

### Hire new instructor
def hire_instructor():
    
    def prompts():
        fac = input("Enter the name of a new faculty member: ")
        fid = input("Enter a new ID for the faculty member: ")
        dep = input("Enter the faculty member's department: ")
        sal = input("Enter the faculty member's salary: ")
        return fac,fid,dep,sal

    conn = psycopg2.connect(dbname="dbinstrux")
    cur = conn.cursor()

    fac,fid,dep,sal = prompts()

    try:
        cur.execute(query, (fid,fac,dep,sal))
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
    student_id = input("Enter a student ID: ")

### Generate course list
def gen_course_list():
    sem = input("Enter the semester: ")
    year = input("Enter the year: ")

### Register a student for a course
def register_student():
    sem = input("Enter the semester: ")
    year = input("Enter the year: ")
    student_id = input("Enter the student ID: ")
    course_id = input("Enter the course ID: ")
    section_id = input("Enter the section ID: ")
# Declare the global variable at the top level of the module
user_id = None

from flask import Flask, render_template, request, redirect, url_for
import pyodbc
from datetime import datetime

#app = Flask(__name__)
app = Flask(__name__, static_folder='c:/Python_Codes/images', static_url_path='/images')

xnow=datetime.now()

# Set up connection to SQL Server database

server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
database = 'MasterDB'
username = 'sa'
password = 'noabrir'
driver = '{SQL Server}'

conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')

server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
database = 'MasterDB'
database_transdb = 'TransDB'
username = 'sa'
password = 'noabrir'
driver = '{SQL Server}'

# Create a connection string
conn_masterdb = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
cursor_masterdb = conn_masterdb.cursor()

@app.route('/')
def login():
    global user_id
    global xnow
    return render_template('login.html')
    

@app.route('/authenticate', methods=['POST'])
def authenticate():
    global user_id
    user_id = request.form['user_id']
    password = request.form['password']
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=? AND Password=?", user_id, password)
    user = cursor.fetchone()
    #print(user)  # Successfully fetched one row (for Admin)
    if user:
        return render_template('welcome.html', user=user)
    else:
        message = 'Invalid login credentials. Please try again.'
        return render_template('message.html', message=message)
		
@app.route('/dashboard')
def dashboard():
    global user_id
    return render_template('dashboard.html')

# STUDENT MENU
@app.route('/student_menu/')
def student_menu():
    global user_id
    return render_template('student_menu.html')
	
@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    global user_id
    global xnow
	
    cursor = conn.cursor()
	
	# Define the SELECT statement
    select_query = 'SELECT ClubName FROM CLUB'
    select_query2 = 'SELECT CampusName FROM CAMPUS'
	
	# Execute the query and fetch the results
    cursor.execute(select_query)
    clubs = [row[0] for row in cursor.fetchall()]
	
    cursor.execute(select_query2)
    campuses = [row[0] for row in cursor.fetchall()]
	
    # Check if the user has permission to access this route
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()

    if not user.CanAddStudent:
        message = 'You are not allowed to run ADD STUDENT. Please see the Administrator.'
        return render_template('student_message.html', message=message)
		
    if request.method == 'POST':
        # Get the student info from the form
        student_number = request.form['student_number']
        fname = request.form['fname']
        lname = request.form['lname']
        mname = request.form['mname']
        bdate = request.form['bdate']
        glevel = request.form['glevel']
        section = request.form['section']
        campus = request.form['campus']
        club = request.form['club']
        cellnumber = request.form['cellnumber']
        address = request.form['address']
        landlinenumber = request.form['landlinenumber']
        fathername = request.form['fathername']
        mothername = request.form['mothername']
        guardianname = request.form['guardianname']
        dormer = request.form.get('dormer') == 'on'
        batch = request.form['batch']
        withspecialneed = request.form.get('withspecialneed') == 'on'
        needdetails = request.form['needdetails']
        '''
        cursor.execute("SELECT * FROM STUDENT")
        rows = cursor.fetchall()
        for row in rows:
           print(row)
		'''
        # Check if a student with the same StudentNumber already exists
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM STUDENT WHERE StudentNumber = ?", student_number)
        row = cursor.fetchone()
        if row:
            # A student with the same StudentNumber already exists
            message = 'A student with Student Number ' + student_number + ' already exists.'
            return render_template('student_message.html', message=message)
        else:
            # No student with the same StudentNumber exists, so insert the new student
            cursor.execute("INSERT INTO STUDENT (StudentNumber,FirstName,FamilyName,MiddleName,BirthDate,GradeLevel,Section,Campus,Club,CellPhoneNumber,Address,LandlineNumber,FatherName,MotherName,GuardianName,Dormer,BatchNumber,WithSpecialNeed,SpecialNeedDetails,CreatedBy,CreatedOn,UpdatedBy,UpdatedOn) VALUES (?, ?, ?, ?, ?, ?, ?,?, ?, ?, ?, ?, ?, ?,?, ?, ?, ?,?, ?, ?, ?, ?)",
              student_number,fname,lname,mname,bdate,glevel,section,campus,club,cellnumber,address,landlinenumber,fathername,mothername,guardianname,dormer,batch,withspecialneed,needdetails,user_id,xnow,user_id,xnow)
            conn.commit()

            message = 'New Student Number ' + student_number + ' added successfully.'
            return render_template('student_message.html', message=message)
		
            return message
 
    # If the request method is GET, show the add student form
    return render_template('student_add.html',clubs=clubs,campuses=campuses)

@app.route('/delete_student', methods=['GET', 'POST'])	
def delete_student():
    global user_id
	# Check if the user has permission to access this route
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()

    if not user.CanDeleteStudent:
        message = 'You are not allowed to run DELETE STUDENT. Please see the Administrator.'
        return render_template('student_message.html', message=message)
		
    if request.method == 'POST':
        # Get the student info from the form
        student_number = request.form['student_number']
		
		# Check if student exists
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM STUDENT WHERE StudentNumber='{student_number}'")
        existing_student = cursor.fetchone()
        if existing_student:
            sql = f"DELETE FROM STUDENT WHERE StudentNumber='{student_number}'"
            cursor.execute(sql)
            conn.commit()
            #return 'Student ' + student_number + ' successfully deleted.'
            message = 'Student ' + student_number + ' successfully deleted.'
            return render_template('student_message.html', message=message)
        else:
            message = 'Student number ' + student_number + ' does not exist.'
            return render_template('student_message.html', message=message)
    return render_template('student_delete.html')
	
@app.route('/update_student1', methods=['GET', 'POST'])
def update_student1():
    global user_id
    global xnow
    cursor = conn.cursor()
	# Check if the user has permission to access this route
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()
    #print(user)	# successful, user has row values
    if not user.CanUpdateStudent:
        message = 'You are not allowed to run UPDATE STUDENT. Please see the Administrator.'
        return render_template('student_message.html', message=message)
    return render_template('update_student1.html')
	
@app.route('/update_student2', methods=['GET', 'POST'])	
def update_student2():
    if request.method == 'POST':
        # Get the student info from the  update_student1 form
        student_number = request.form['student_number']
    cursor = conn.cursor()
	
	# Define the SELECT statement
    select_query = 'SELECT ClubName FROM CLUB'
    select_query2 = 'SELECT CampusName FROM CAMPUS'
	
	# Execute the query and fetch the results
    cursor.execute(select_query)
    clubs = [row[0] for row in cursor.fetchall()]
	
    cursor.execute(select_query2)
    campuses = [row[0] for row in cursor.fetchall()]
	
    cursor.execute("SELECT * FROM STUDENT WHERE StudentNumber = ?", student_number)
    student = cursor.fetchone()
    return render_template('update_student2.html',clubs=clubs,campuses=campuses,student=student)

@app.route('/update_student', methods=['GET', 'POST'])
def update_student():
    global user_id
    global xnow
    cursor = conn.cursor()
	
	# Define the SELECT statement
    select_query = 'SELECT ClubName FROM CLUB'
    select_query2 = 'SELECT CampusName FROM CAMPUS'
	
	# Execute the query and fetch the results
    cursor.execute(select_query)
    clubs = [row[0] for row in cursor.fetchall()]
	
    cursor.execute(select_query2)
    campuses = [row[0] for row in cursor.fetchall()]

    # Check if the user has permission to access this route
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()
    #print(user)    # successful, user has values
    if not user.CanUpdateStudent:
        message = 'You are not allowed to run UPDATE STUDENT. Please see the Administrator.'
        return render_template('student_message.html', message=message)
		
    if request.method == 'POST':
        # Get the student info from the form
        student_number = request.form['student_number']
        fname = request.form['fname']
        lname = request.form['lname']
        mname = request.form['mname']
        bdate = request.form['bdate']
        glevel = request.form['glevel']
        section = request.form['section']
        campus = request.form['campus']
        club = request.form['club']
        cellnumber = request.form['cellnumber']
        address = request.form['address']
        landlinenumber = request.form['landlinenumber']
        fathername = request.form['fathername']
        mothername = request.form['mothername']
        guardianname = request.form['guardianname']
        dormer = request.form.get('dormer') == 'on'
        batch = request.form['batch']
        withspecialneed = request.form.get('withspecialneed') == 'on'
        needdetails = request.form['needdetails']
        '''
        cursor.execute("SELECT * FROM STUDENT")
        rows = cursor.fetchall()
        for row in rows:
           print(row)
		'''
        # Check if a student with the same StudentNumber already exists
		
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM STUDENT WHERE StudentNumber = ?", student_number)
        existing_student = cursor.fetchone()
        student = existing_student
		
        if existing_student:
            update_query = "UPDATE STUDENT SET FirstName=?,FamilyName=?,MiddleName=?,BirthDate=?,GradeLevel=?,Section=?,Campus=?,Club=?,CellPhoneNumber=?,Address=?,LandlineNumber=?,FatherName=?,MotherName=?,GuardianName=?,Dormer=?,BatchNumber=?,WithSpecialNeed=?,SpecialNeedDetails=?,CreatedBy=?,CreatedOn=?,UpdatedBy=?,UpdatedOn=? WHERE StudentNumber=?"
            cursor.execute(update_query, (fname,lname,mname,bdate,glevel,section,campus,club,cellnumber,address,landlinenumber,fathername,mothername,guardianname,dormer,batch,withspecialneed,needdetails,'user_id',xnow,'user_id',xnow,student_number,))
            conn.commit()
            message = 'Student number ' + student_number + ' successfully updated..'
            return render_template('student_message.html', message=message)
        else:
            message = 'Student number ' + student_number + ' does not exist.'
            return render_template('student_message.html', message=message)
        
    # If the request method is GET, show the add student form
    return render_template('update_student1.html',clubs=clubs,campuses=campuses)

	
@app.route('/query_student', methods=['GET', 'POST'])	
def query_student():
    global user_id
    #print (user_id)	# user_id=TestUser
    # Check if the user has permission to access this route
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()

    if not user.CanQueryStudent:
        message = 'You are not allowed to run QUERY STUDENT. Please see the Administrator.'
        return render_template('student_message.html', message=message)

    if request.method == 'POST':
        student_number = request.form['student_number']
        cursor.execute(f"SELECT * FROM STUDENT WHERE StudentNumber='{student_number}'")
        existing_student = cursor.fetchone()

        if existing_student:
            student=existing_student
            xstudent=student.BirthDate
            year = xstudent.strftime("%Y")
            month = xstudent.strftime("%m")
            day = xstudent.strftime("%d")
            xbirthdate=year + '-' + month + '-' + day
            student.BirthDate = xbirthdate 

            return render_template('student.html', student=existing_student)
        else:
           message = 'Student number ' + student_number + ' does not exist.'
           return render_template('student_message.html', message=message)
    return render_template('student_query.html')
	
@app.route('/display_students/')
def display_students():
    global user_id
    #print(user_id)  # successful  - Admin

    # Check if the user has permission to access this route
	# Set up connection to SQL Server database
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()
    print(user)
    if not user.CanDisplayStudent:
        message = 'You are not allowed to run DISPLAY STUDENTS. Please see the Administrator.'
        return render_template('student_message.html', message=message)
    else:
        exec(open('display_stu.py').read())
        return '-DISPLAY STUDENTS got clicked-'
		
#if __name__ == '__main__':      # commented on 7-26-2023 7:15pm
#    app.run()

	
# TEACHER MENU
@app.route('/')  # inserted on 7-26-2023 7:17pm
@app.route('/teacher_menu/')
#@app.route('/teacher_menu/', endpoint='teacher_menu')
def teacher_menu():
    global user_id
    return render_template('teacher_menu.html')

@app.route('/add_teacher', methods=['GET', 'POST'])
def add_teacher():
    global xnow
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()
	
    if not user.CanAddTeacher:
        message = 'You are not allowed to run ADD TEACHER. Please see the Administrator.'
        return render_template('teacher_message.html', message=message)
		
    if request.method == 'POST':
        # Get the teacher info from the form
        teacher_id = request.form['teacher_id']
        teacher_name = request.form['teacher_name']
        rank = request.form['rank']
        cdegree = request.form['cdegree']
        mdegree = request.form['mdegree']
        ddegree = request.form['ddegree']
        campus = request.form['campus']
        email_address = request.form['email_address']
        '''
        cursor.execute("SELECT * FROM TEACHER")
        rows = cursor.fetchall()
        for row in rows:
           print(row)
		'''
        # Check if a teacher with the same TeacherID already exists
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM TEACHER WHERE TeacherID = ?", teacher_id)
        row = cursor.fetchone()
        if row:
            # A teacher with the same TeacherID already exists
            message = 'A teacher with TeacherID ' + teacher_id + ' already exists.'
            return render_template('teacher_message.html', message=message)
        else:
            # No teacher with the same TeacherID exists, so insert the new teacher
            cursor.execute("INSERT INTO TEACHER (TeacherID,TeacherName,Rank,CollegeDegree,MasteralDegree,DoctoralDegree,Campus,EmailAddress,CreatedBy,CreatedOn,UpdatedBy,UpdatedOn) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
              teacher_id,teacher_name,rank,cdegree,mdegree,ddegree,campus,email_address,'Vin',xnow,'Vin',xnow)
            conn.commit()

            message = 'New Teacher ID ' + teacher_id + ' added successfully.'
            return render_template('teacher_message.html', message=message)
			
            #return message
  
    # If the request method is GET, show the add teacher form
    return render_template('teacher_add.html')

@app.route('/delete_teacher', methods=['GET', 'POST'])	
def delete_teacher():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()
    if not user.CanDeleteTeacher:
        message = 'You are not allowed to run DELETE TEACHER. Please see the Administrator.'
        return render_template('teacher_message.html', message=message)
		
    if request.method == 'POST':
        # Get the teacher info from the form
        teacher_id = request.form['teacher_id']
		
		# Check if teacher exists
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM TEACHER WHERE TeacherID='{teacher_id}'")
        existing_teacher = cursor.fetchone()
        if existing_teacher:
            sql = f"DELETE FROM TEACHER WHERE TeacherID='{teacher_id}'"
            cursor.execute(sql)
            conn.commit()
            #return 'Teacher ' + teacher_id + ' successfully deleted.'
            message = 'Teacher ID ' + teacher_id + ' successfully deleted.'
            return render_template('teacher_message.html', message=message)
        else:
            message = 'Teacher ID ' + teacher_id + ' does not exist.'
            return render_template('teacher_message.html', message=message)
    return render_template('teacher_delete.html')
	
	
@app.route('/update_teacher1', methods=['GET', 'POST'])
def update_teacher1():
    global user_id
    global xnow
    cursor = conn.cursor()
    return render_template('update_teacher1.html')
	
@app.route('/update_teacher2', methods=['GET', 'POST'])	
def update_teacher2():
    if request.method == 'POST':

        teacher_id = request.form['teacher_id']
    
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')	
    cursor = conn.cursor()
    
    # Define the SELECT statement
    select_query2 = 'SELECT CampusCode,CampusName FROM CAMPUS'
    
    # Execute the query and fetch the results
    cursor.execute(select_query2)
    campuses = [(row[0], row[1]) for row in cursor.fetchall()]
    #print(campuses)   #successful
    
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    cursor = conn.cursor()
	
    cursor.execute("SELECT * FROM TEACHER WHERE TeacherID = ?", teacher_id)
    teacher = cursor.fetchone()

    return render_template('update_teacher2.html',teacher=teacher,campuses=campuses)

@app.route('/update_teacher', methods=['GET', 'POST'])
def update_teacher():
    global user_id
    global xnow
    cursor = conn.cursor()
		
    if request.method == 'POST':
        # Get the subject info from the form
        teacher_id = request.form['teacher_id']
        teacher_name = request.form['teacher_name']
        rank = request.form['rank']
        college_degree = request.form['college_degree']
        masteral_degree = request.form['masteral_degree']
        doctoral_degree = request.form['doctoral_degree']
        campus = request.form['campus']
        email_address = request.form['email_address']
        '''
        cursor.execute("SELECT * FROM TEACHER")
        rows = cursor.fetchall()
        for row in rows:
           print(row)
		'''
        # Check if a club with the same ClubCode already exists
		
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM TEACHER WHERE TeacherID = ?", teacher_id)
        existing_teacher = cursor.fetchone()
        teacher = existing_teacher
        #print(teacher)
        if existing_teacher:
            update_query = "UPDATE TEACHER SET TeacherName=?,Rank=?,CollegeDegree=?,MasteralDegree=?,DoctoralDegree=?,Campus=?,EmailAddress=?,CreatedBy=?,CreatedOn=?,UpdatedBy=?,UpdatedOn=? WHERE TeacherID=?"
            cursor.execute(update_query, (teacher_name,rank,college_degree,masteral_degree,doctoral_degree,campus,email_address,user_id,xnow,user_id,xnow,teacher_id,))
            conn.commit()
            message = 'TeacherID ' + teacher_id + ' successfully updated..'
            return render_template('teacher_message.html', message=message)
        else:
            message = 'TeacherID ' + teacher_id + ' does not exist.'
            return render_template('teacher_message.html', message=message)
        
    # If the request method is GET, show the add club form
    return render_template('update_teacher1.html')
	
@app.route('/query_teacher', methods=['GET', 'POST'])
def query_teacher():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()
    if not user.CanQueryTeacher:
        message = 'You are not allowed to run QUERY TEACHER. Please see the Administrator.'
        return render_template('teacher_message.html', message=message)
    if request.method == 'POST':
        teacher_id = request.form['teacher_id']
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM TEACHER WHERE TeacherID='{teacher_id}'")
        existing_teacher = cursor.fetchone()
        #print(existing_teacher)
        if existing_teacher:
            teacher=existing_teacher			
            return render_template('teacher.html', teacher=existing_teacher)
        else:
           message = 'Teacher ID ' + teacher_id + ' does not exist.'
           return render_template('teacher_message.html', message=message)
    return render_template('teacher_query.html')
	
@app.route('/display_teachers/')
def display_teachers():
    # Set up connection to SQL Server database
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()

    if not user.CanDisplayTeacher:
        message = 'You are not allowed to run DISPLAY TEACHERS. Please see the Administrator.'
        return render_template('teacher_message.html', message=message)
    else:
        exec(open('display_teachers.py').read())
        return '-DISPLAY TEACHERS got clicked-'
   
# ADMIN MENU
@app.route('/')  
@app.route('/admin_menu/')
#@app.route('/admin_menu/', endpoint='teacher_menu')
def admin_menu():
    global user_id
    #return render_template('admin_menu.html')
    return render_template('admin_menu.html', user_id=user_id)
	
@app.route('/add_admin', methods=['GET', 'POST'])
def add_admin():
    global xnow
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()
    if not user.CanAddAdmin:
        message = 'You are not allowed to run ADD ADMIN. OFFICER. Please see the Administrator.'
        return render_template('admin_message.html', message=message)
    if request.method == 'POST':
        # Get the admin info from the form
        admin_code = request.form['admin_code']
        admin_name = request.form['admin_name']
        dept = request.form['dept']
        division = request.form['division']
        position_title = request.form['position_title']
        email_add = request.form['email_add']
        cell_number = request.form['cell_number']
        landline_number = request.form['landline_number']
        '''
        cursor.execute("SELECT * FROM ADMIN")
        rows = cursor.fetchall()
        for row in rows:
           print(row)
		'''
        # Check if a AdminCode with the same AdminCode already exists
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ADMIN WHERE AdminCode = ?", admin_code)
        row = cursor.fetchone()
        
        if row:
            # A admin with the same admin_code already exists
            message = 'A admin with AdminCode ' + admin_code + ' already exists.'
            return render_template('admin_message.html', message=message)
        else:
            # No admin with the same AdminCode exists, so insert the new admin
            cursor.execute("INSERT INTO ADMIN (AdminCode,AdminOfficerName,Department,Division,PositionTitle,EmailAddress,CellphoneNumber,LandlineNumber,CreatedBy,CreatedOn,UpdatedBy,UpdatedOn) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
              admin_code,admin_name,dept,division,position_title,email_add,cell_number,landline_number,'TestUser',xnow,'TestUser',xnow)
            conn.commit()

            message = 'New admin code ' + admin_code + ' added successfully.'
            return render_template('admin_message.html', message=message)
		
            return message
 
    # If the request method is GET, show the add admin form
    return render_template('admin_add.html')

@app.route('/delete_admin', methods=['GET', 'POST'])	
def delete_admin():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()
    if not user.CanDeleteAdmin:
        message = 'You are not allowed to run DELETE ADMIN. Please see the Administrator.'
        return render_template('admin_message.html', message=message)
    if request.method == 'POST':
        # Get the admin info from the form
        admin_code = request.form['admin_code']
		
		# Check if admin exists
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM ADMIN WHERE AdminCode='{admin_code}'")
        existing_admin = cursor.fetchone()
        if existing_admin:
            sql = f"DELETE FROM ADMIN WHERE AdminCode='{admin_code}'"
            cursor.execute(sql)
            conn.commit()
            message = 'Admin ' + admin_code + ' successfully deleted.'
            return render_template('admin_message.html', message=message)
        else:
            message = 'Admin code ' + admin_code + ' does not exist.'
            return render_template('admin_message.html', message=message)
    return render_template('admin_delete.html')
	
@app.route('/update_admin1', methods=['GET', 'POST'])
def update_admin1():
    global user_id
    global xnow
    cursor = conn.cursor()
    return render_template('update_admin1.html')
	
@app.route('/update_admin2', methods=['GET', 'POST'])	
def update_admin2():
    if request.method == 'POST':
        # Get the section info from the  update_section1 form
        admin_code = request.form['admin_code']
    
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')	
    cursor = conn.cursor()
    
    # Define the SELECT statement
    select_query2 = 'SELECT CampusCode,CampusName FROM CAMPUS'
    
    # Execute the query and fetch the results
    cursor.execute(select_query2)
    campuses = [(row[0], row[1]) for row in cursor.fetchall()]
    #print(campuses)   #successful
    
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    cursor = conn.cursor()
	
    cursor.execute("SELECT * FROM ADMIN WHERE AdminCode = ?", admin_code)
    admin = cursor.fetchone()

    return render_template('update_admin2.html',admin=admin,campuses=campuses)

@app.route('/update_admin', methods=['GET', 'POST'])
def update_admin():
    global user_id
    global xnow
    cursor = conn.cursor()
		
    if request.method == 'POST':
        # Get the subject info from the form
        admin_code = request.form['admin_code']
        admin_officer_name = request.form['admin_officer_name']
        division = request.form['division']
        position_title = request.form['position_title']
        campus = request.form['campus']
        email_address = request.form['email_address']
        cellphone_number = request.form['cellphone_number']
        landline_number = request.form['landline_number']
        '''
        cursor.execute("SELECT * FROM ADMIN")
        rows = cursor.fetchall()
        for row in rows:
           print(row)
		'''
        # Check if a subject the same SubjectCode already exists
		
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ADMIN WHERE AdminCode = ?", admin_code)
        existing_admin = cursor.fetchone()
        admin = existing_admin
		
        if existing_admin:
            update_query = "UPDATE ADMIN SET AdminOfficerName=?,Division=?,PositionTitle=?,EmailAddress=?,CellphoneNumber=?,LandlineNumber=?,Campus=?,CreatedBy=?,CreatedOn=?,UpdatedBy=?,UpdatedOn=? WHERE AdminCode=?"
            cursor.execute(update_query, (admin_officer_name,division,position_title,campus,email_address,cellphone_number,landline_number,user_id,xnow,user_id,xnow,admin_code,))
            conn.commit()
            message = 'Admin Code ' + admin_code + ' successfully updated..'
            return render_template('admin_message.html', message=message)
        else:
            message = 'Section code ' + section_code + ' does not exist.'
            return render_template('admin_message.html', message=message)
        
    # If the request method is GET, show the add section form
    return render_template('update_admin1.html')
	
@app.route('/query_admin', methods=['GET', 'POST'])
def query_admin():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()
    if not user.CanQueryAdmin:
        message = 'You are not allowed to run QUERY ADMIN. Please see the Administrator.'
        return render_template('admin_message.html', message=message)
    if request.method == 'POST':
        admin_code = request.form['admin_code']
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM ADMIN WHERE AdminCode='{admin_code}'")
        existing_admin = cursor.fetchone()
        #print(existing_admin)
        if existing_admin:
            admin=existing_admin
            return render_template('admin.html', admin=existing_admin)
        else:
           message = 'Admin code ' + admin_code + ' does not exist.'
           return render_template('message.html', message=message)
    return render_template('admin_query.html')
	
@app.route('/display_admin/')
def display_admin():
    global user_id
    # Set up connection to SQL Server database
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()

    if not user.CanDisplayAdmin:
        message = 'You are not allowed to run DISPLAY ADMIN. Please see the Administrator.'
        return render_template('admin_message.html', message=message)
    else:
        exec(open('admin_display.py').read())
        return '-DISPLAY ADMIN got clicked-'
  
# SUBJECT MENU
@app.route('/')  
@app.route('/subject_menu/')
#@app.route('/subject_menu/', endpoint='teacher_menu')
def subject_menu():
    global user_id
    return render_template('subject_menu.html', user_id=user_id)
	
@app.route('/add_subject', methods=['GET', 'POST'])
def add_subject():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()
    if not user.CanAddSubject:
        message = 'You are not allowed to run ADD SUBJECT. Please see the Administrator.'
        return render_template('subject_message.html', message=message)
		
    if request.method == 'POST':
        # Get the subject info from the form
        subject_code = request.form['subject_code']
        subject_name = request.form['subject_name']
        glevel = request.form['glevel']
        dept = request.form['dept']
        course = request.form['course']
        campus = request.form['campus']
        quiz_weight = request.form['quiz_weight']
        formative_weight = request.form['formative_weight']
        alternative_weight = request.form['alternative_weight']
        perio_weight = request.form['perio_weight']
        '''
        cursor.execute("SELECT * FROM SUBJECT")
        rows = cursor.fetchall()
        for row in rows:
           print(row)
		'''
        # Check if a SubjectCode with the same SubjectCode already exists
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM SUBJECT WHERE SubjectCode = ?", subject_code)
        row = cursor.fetchone()
        
        if row:
            # A subject with the same subject_code already exists
            message = 'A subject with SubjectCode ' + subject_code + ' already exists.'
            return render_template('subject_message.html', message=message)
        else:
            # No subject with the same SubjectCode exists, so insert the new subject
            cursor.execute("INSERT INTO SUBJECT (SubjectCode,SubjectName,GradeLevel,Department,Course,Campus,QuizWeight,FormativeWeight,AlternativeWeight,PerioWeight,CreatedBy,CreatedOn,UpdatedBy,UpdatedOn) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
              subject_code,subject_name,glevel,dept,course,campus,quiz_weight,formative_weight,alternative_weight,perio_weight,user_id,xnow,user_id,xnow)
            conn.commit()

            message = 'New subject code ' + subject_code + ' added successfully.'
            return render_template('subject_message.html', message=message)
		
            return message

    # If the request method is GET, show the add subject form
    return render_template('subject_add.html')

@app.route('/delete_subject', methods=['GET', 'POST'])	
def delete_subject():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()
    if not user.CanDeleteSubject:
        message = 'You are not allowed to run DELETE SUBJECT. Please see the Administrator.'
        return render_template('subject_message.html', message=message)
    if request.method == 'POST':
        # Get the subject info from the form
        subject_code = request.form['subject_code']
		
		# Check if subject exists
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM SUBJECT WHERE SubjectCode='{subject_code}'")
        existing_subject = cursor.fetchone()
        if existing_subject:
            sql = f"DELETE FROM SUBJECT WHERE SubjectCode='{subject_code}'"
            cursor.execute(sql)
            conn.commit()
            message = 'Subject ' + subject_code + ' successfully deleted.'
            return render_template('subject_message.html', message=message)
        else:
            message = 'Subject code ' + subject_code + ' does not exist.'
            return render_template('subject_message.html', message=message)
    return render_template('subject_delete.html')
	
@app.route('/update_subject1', methods=['GET', 'POST'])
def update_subject1():
    global user_id
    global xnow
    cursor = conn.cursor()
    return render_template('update_subject1.html')
	
@app.route('/update_subject2', methods=['GET', 'POST'])	
def update_subject2():
    if request.method == 'POST':
        # Get the subject info from the  update_subject1 form
        subject_code = request.form['subject_code']
    
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')	
    cursor = conn.cursor()
    
    # Define the SELECT statement
    select_query2 = 'SELECT CampusCode,CampusName FROM CAMPUS'
    
    # Execute the query and fetch the results
    cursor.execute(select_query2)
    campuses = [(row[0], row[1]) for row in cursor.fetchall()]
    #print(campuses)   #successful
    
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    cursor = conn.cursor()
	
    cursor.execute("SELECT * FROM SUBJECT WHERE SubjectCode = ?", subject_code)
    subject = cursor.fetchone()

    return render_template('update_subject2.html',subject=subject,campuses=campuses)

@app.route('/update_subject', methods=['GET', 'POST'])
def update_subject():
    global user_id
    global xnow
    cursor = conn.cursor()
		
    if request.method == 'POST':
        # Get the subject info from the form
        subject_code = request.form['subject_code']
        subject_name = request.form['subject_name']
        glevel = request.form['glevel']
        dept = request.form['department']
        course = request.form['course']
        campus = request.form['campus']
        quiz_weight = request.form['quiz_weight']
        formative_weight = request.form['formative_weight']
        alternative_weight = request.form['alternative_weight']
        perio_weight = request.form['perio_weight']
        '''
        cursor.execute("SELECT * FROM SUBJECT")
        rows = cursor.fetchall()
        for row in rows:
           print(row)
		'''
        # Check if a subject the same SubjectCode already exists
		
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM SUBJECT WHERE SubjectCode = ?", subject_code)
        existing_subject = cursor.fetchone()
        subject = existing_subject
		
        if existing_subject:
            update_query = "UPDATE SUBJECT SET SubjectName=?,GradeLevel=?,Department=?,Course=?,Campus=?,QuizWeight=?,FormativeWeight=?,AlternativeWeight=?,PerioWeight=?,CreatedBy=?,CreatedOn=?,UpdatedBy=?,UpdatedOn=? WHERE SubjectCode=?"
            cursor.execute(update_query, (subject_name,glevel,dept,course,campus,quiz_weight,formative_weight,alternative_weight,perio_weight,user_id,xnow,user_id,xnow,subject_code,))
            conn.commit()
            message = 'Subject code ' + subject_code + ' successfully updated..'
            return render_template('subject_message.html', message=message)
        else:
            message = 'Subject code ' + subject_code + ' does not exist.'
            return render_template('subject_message.html', message=message)
        
    # If the request method is GET, show the add subject form
    return render_template('update_subject1.html')
	
@app.route('/query_subject', methods=['GET', 'POST'])
def query_subject():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()
    if not user.CanQuerySubject:
        message = 'You are not allowed to run QUERY SUBJECT. Please see the Administrator.'
        return render_template('subject_message.html', message=message)
    if request.method == 'POST':
        subject_code = request.form['subject_code']
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM SUBJECT WHERE SubjectCode='{subject_code}'")
        existing_subject = cursor.fetchone()
        #print(existing_subject)
        if existing_subject:
            subject=existing_subject
            return render_template('subject.html', subject=existing_subject)
        else:
           message = 'Subject code ' + subject_code + ' does not exist.'
           return render_template('message.html', message=message)
    return render_template('subject_query.html')
	
@app.route('/display_subjects/')
def display_subjects():
   # Set up connection to SQL Server database
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()

    if not user.CanDisplaySubject:
        message = 'You are not allowed to run DISPLAY SUBJECTS. Please see the Administrator.'
        return render_template('subject_message.html', message=message)
    else:
        exec(open('display_subjects.py').read())
        return '-DISPLAY SUBJECTS got clicked-'
		
		
# SECTION MENU
@app.route('/')  
@app.route('/section_menu/')

def section_menu():
    global user_id
    return render_template('section_menu.html', user_id=user_id)
	
@app.route('/add_section', methods=['GET', 'POST'])
def add_section():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()
    if not user.CanAddSubject:
        message = 'You are not allowed to run ADD SECTION. Please see the Administrator.'
        return render_template('section_message.html', message=message)
		
    if request.method == 'POST':
        # Get the subject info from the form
        section_code = request.form['section_code']
        section_name = request.form['section_name']
        glevel = request.form['glevel']
        campus_code = request.form['campus_code']
        adviser_name = request.form['adviser_name']
        '''
        cursor.execute("SELECT * FROM SECTION")
        rows = cursor.fetchall()
        for row in rows:
           print(row)
		'''
        # Check if a SubjectCode with the same SubjectCode already exists
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM SECTION WHERE SectionCode = ?", section_code)
        row = cursor.fetchone()
        
        if row:
            # A subject with the same section_code already exists
            message = 'A section with SectionCode ' + section_code + ' already exists.'
            return render_template('section_message.html', message=message)
        else:
            # No subject with the same SectionCode exists, so insert the new section
            cursor.execute("INSERT INTO SECTION (SectionCode,SectionName,CampusCode,GradeLevel,AdviserName,CreatedBy,CreatedOn,UpdatedBy,UpdatedOn) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
              section_code,section_name,campus_code,glevel,adviser_name,user_id,xnow,user_id,xnow)
            conn.commit()

            message = 'New section code ' + section_code + ' added successfully.'
            return render_template('section_message.html', message=message)
		
            #return message

    # If the request method is GET, show the add subject form
    return render_template('section_add.html')

@app.route('/delete_section', methods=['GET', 'POST'])	
def delete_section():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()
    if not user.CanDeleteSection:
        message = 'You are not allowed to run DELETE SECTION. Please see the Administrator.'
        return render_template('section_message.html', message=message)
    if request.method == 'POST':
        # Get the section info from the form
        section_code = request.form['section_code']
		
		# Check if section exists
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM SECTION WHERE SectionCode='{section_code}'")
        existing_section = cursor.fetchone()
        if existing_section:
            sql = f"DELETE FROM SECTION WHERE SectionCode='{section_code}'"
            cursor.execute(sql)
            conn.commit()
            message = 'Section ' + section_code + ' successfully deleted.'
            return render_template('section_message.html', message=message)
        else:
            message = 'Section code ' + section_code + ' does not exist.'
            return render_template('section_message.html', message=message)
    return render_template('section_delete.html')
	
@app.route('/update_section1', methods=['GET', 'POST'])
def update_section1():
    global user_id
    global xnow
    cursor = conn.cursor()
    return render_template('update_section1.html')
	
@app.route('/update_section2', methods=['GET', 'POST'])	
def update_section2():
    if request.method == 'POST':
        # Get the section info from the  update_section1 form
        section_code = request.form['section_code']
    
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')	
    cursor = conn.cursor()
    
    # Define the SELECT statement
    select_query2 = 'SELECT CampusCode,CampusName FROM CAMPUS'
    
    # Execute the query and fetch the results
    cursor.execute(select_query2)
    campuses = [(row[0], row[1]) for row in cursor.fetchall()]
    #print(campuses)   #successful
    
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    cursor = conn.cursor()
	
    cursor.execute("SELECT * FROM SECTION WHERE SectionCode = ?", section_code)
    section = cursor.fetchone()

    return render_template('update_section2.html',section=section,campuses=campuses)

@app.route('/update_section', methods=['GET', 'POST'])
def update_section():
    global user_id
    global xnow
    cursor = conn.cursor()
		
    if request.method == 'POST':
        # Get the section info from the form
        section_code = request.form['section_code']
        section_name = request.form['section_name']
        glevel = request.form['glevel']
        adviser_name = request.form['adviser_name']
        campus_code = request.form['campus_code']
        '''
        cursor.execute("SELECT * FROM SECTION")
        rows = cursor.fetchall()
        for row in rows:
           print(row)
		'''
        # Check if a section the same SectionCode already exists
		
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM SECTION WHERE SectionCode = ?", section_code)
        existing_section = cursor.fetchone()
        section = existing_section
		
        if existing_section:
            update_query = "UPDATE SECTION SET SectionName=?,CampusCode=?,GradeLevel=?,AdviserName=?,CreatedBy=?,CreatedOn=?,UpdatedBy=?,UpdatedOn=? WHERE SectionCode=?"
            cursor.execute(update_query, (section_name,campus_code,glevel,adviser_name,user_id,xnow,user_id,xnow,section_code,))
            conn.commit()
            message = 'section code ' + section_code + ' successfully updated..'
            return render_template('section_message.html', message=message)
        else:
            message = 'Section code ' + section_code + ' does not exist.'
            return render_template('section_message.html', message=message)
        
    # If the request method is GET, show the add section form
    return render_template('update_section1.html')
	
@app.route('/query_section', methods=['GET', 'POST'])
def query_section():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()
    if not user.CanQuerySection:
        message = 'You are not allowed to run QUERY SECTION. Please see the Administrator.'
        return render_template('section_message.html', message=message)
    if request.method == 'POST':
        section_code = request.form['section_code']
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM SECTION WHERE SectionCode='{section_code}'")
        existing_section = cursor.fetchone()
        #print(existing_section)
        if existing_section:
            section=existing_section
            return render_template('section.html', section=existing_section)
        else:
           message = 'Section code ' + section_code + ' does not exist.'
           return render_template('section_message.html', message=message)
    return render_template('section_query.html')
	
@app.route('/display_sections/')
def display_sections():
   # Set up connection to SQL Server database
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()

    if not user.CanDisplaySection:
        message = 'You are not allowed to run DISPLAY SECTIONS. Please see the Administrator.'
        return render_template('section_message.html', message=message)
    else:
        exec(open('display_sections.py').read())
        return '-DISPLAY SECTIONS got clicked-'
		
# CAMPUS MENU
@app.route('/')  
@app.route('/campus_menu/')

def campus_menu():
    global user_id
    return render_template('campus_menu.html', user_id=user_id)
	
@app.route('/add_campus', methods=['GET', 'POST'])
def add_campus():
    global user_id
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()
    if not user.CanAddCampus:
        message = 'You are not allowed to run ADD CAMPUS. Please see the Administrator.'
        return render_template('campus_message.html', message=message)
		
    if request.method == 'POST':
        # Get the subject info from the form
        campus_code = request.form['campus_code']
        campus_name = request.form['campus_name']
        director_name = request.form['director_name']
        address = request.form['address']
        web_site = request.form['web_site']
        cell_phone_number = request.form['cell_phone_number']
        landline_number = request.form['landline_number']
        '''
        cursor.execute("SELECT * FROM CAMPUS")
        rows = cursor.fetchall()
        for row in rows:
           print(row)
		'''
        # Check if a SubjectCode with the same SubjectCode already exists
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM CAMPUS WHERE CampusCode = ?", campus_code)
        row = cursor.fetchone()
        
        if row:
            # A subject with the same section_code already exists
            message = 'A campus with CampusCode ' + campus_code + ' already exists.'
            return render_template('campus_message.html', message=message)
        else:
            # No subject with the same CampusCode exists, so insert the new section
            cursor.execute("INSERT INTO CAMPUS (CampusCode,CampusName,DirectorName,Address,WebSite,CellPhoneNumber,LandlineNumber,CreatedBy,CreatedOn,UpdatedBy,UpdatedOn) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
              campus_code,campus_name,director_name,address,web_site,cell_phone_number,landline_number,user_id,xnow,user_id,xnow)
            conn.commit()

            message = 'New Campus code ' + campus_code + ' added successfully.'
            return render_template('campus_message.html', message=message)
		
            #return message

    # If the request method is GET, show the add campus form
    return render_template('campus_add.html')

@app.route('/delete_campus', methods=['GET', 'POST'])	
def delete_campus():
    global user_id
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()
    if not user.CanDeleteCampus:
        message = 'You are not allowed to run DELETE CAMPUS. Please see the Administrator.'
        return render_template('campus_message.html', message=message)
    if request.method == 'POST':
        # Get the campus info from the form
        campus_code = request.form['campus_code']
		
		# Check if campus exists
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM CAMPUS WHERE CampusCode='{campus_code}'")
        existing_campus = cursor.fetchone()
        if existing_campus:
            sql = f"DELETE FROM CAMPUS WHERE CampusCode='{campus_code}'"
            cursor.execute(sql)
            conn.commit()
            message = 'Campus ' + campus_code + ' successfully deleted.'
            return render_template('campus_message.html', message=message)
        else:
            message = 'Campus code ' + campus_code + ' does not exist.'
            return render_template('campus_message.html', message=message)
    return render_template('campus_delete.html')
	
@app.route('/update_campus1', methods=['GET', 'POST'])
def update_campus1():
    global user_id
    global xnow
    cursor = conn.cursor()
    return render_template('update_campus1.html')
	
@app.route('/update_campus2', methods=['GET', 'POST'])	
def update_campus2():
    if request.method == 'POST':
        # Get the campus info from the  update_section1 form
        campus_code = request.form['campus_code']
    
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')	
    cursor = conn.cursor()
 
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    cursor = conn.cursor()
	
    cursor.execute("SELECT * FROM CAMPUS WHERE CampusCode = ?", campus_code)
    campus = cursor.fetchone()

    return render_template('update_campus2.html',campus=campus)

@app.route('/update_campus', methods=['GET', 'POST'])
def update_campus():
    global user_id
    global xnow
    cursor = conn.cursor()
		
    if request.method == 'POST':
        # Get the campus info from the form
        campus_code = request.form['campus_code']
        campus_name = request.form['campus_name']
        director_name = request.form['director_name']
        address = request.form['address']
        web_site = request.form['web_site']
        cell_phone_number = request.form['cell_phone_number']
        landline_number = request.form['landline_number']
        '''
        cursor.execute("SELECT * FROM CAMPUS")
        rows = cursor.fetchall()
        for row in rows:
           print(row)
		'''
        # Check if a subject the same SubjectCode already exists
		
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM CAMPUS WHERE CampusCode = ?", campus_code)
        existing_campus = cursor.fetchone()
        campus = existing_campus
		
        if existing_campus:
            update_query = "UPDATE CAMPUS SET CampusName=?,DirectorName=?,Address=?,WebSite=?,CellPhoneNumber=?,LandlineNumber=?,CreatedBy=?,CreatedOn=?,UpdatedBy=?,UpdatedOn=? WHERE CampusCode=?"
            cursor.execute(update_query, (campus_name,director_name,address,web_site,cell_phone_number,landline_number,user_id,xnow,user_id,xnow,campus_code,))
            conn.commit()
            message = 'Campus code ' + campus_code + ' successfully updated..'
            return render_template('campus_message.html', message=message)
        else:
            message = 'Campus code ' + campus_code + ' does not exist.'
            return render_template('campus_message.html', message=message)
        
    # If the request method is GET, show the add campus form
    return render_template('update_campus1.html')
	
@app.route('/query_campus', methods=['GET', 'POST'])
def query_campus():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()
    if not user.CanQueryCampus:
        message = 'You are not allowed to run QUERY CAMPUS. Please see the Administrator.'
        return render_template('campus_message.html', message=message)
    if request.method == 'POST':
        campus_code = request.form['campus_code']
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM CAMPUS WHERE CampusCode='{campus_code}'")
        existing_campus = cursor.fetchone()
        #print(existing_campus)
        if existing_campus:
            section=existing_campus
            return render_template('campus.html', campus=existing_campus)
        else:
           message = 'Campus code ' + campus_code + ' does not exist.'
           return render_template('campus_message.html', message=message)
    return render_template('campus_query.html')
	
@app.route('/display_campuses/')
def display_campuses():
   # Set up connection to SQL Server database
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()

    if not user.CanDisplayCampus:
        message = 'You are not allowed to run DISPLAY CAMPUSES. Please see the Administrator.'
        return render_template('campus_message.html', message=message)
    else:
        exec(open('display_campuses.py').read())
        return '-DISPLAY CAMPUSES got clicked-'
		
# NOTIFICATION MENU
@app.route('/')  
@app.route('/notification_menu/')

def notification_menu():
    global user_id
    return render_template('notification_menu.html', user_id=user_id)
	
@app.route('/add_notification', methods=['GET', 'POST'])
def add_notification():
    global user_id
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()
    if not user.CanAddNotification:
        message = 'You are not allowed to run ADD NOTIFICATION. Please see the Administrator.'
        return render_template('notification_message.html', message=message)
		
    if request.method == 'POST':
        # Get the notification info from the form
        noti_code = request.form['noti_code']
        noti_date = request.form['noti_date']
        noti_sender = request.form['noti_sender']
        noti_receiver1 = request.form['noti_receiver1']
        noti_receiver2 = request.form['noti_receiver2']
        noti_subject = request.form['noti_subject']
        campus = request.form['campus']
        sender_email = request.form['sender_email']
        receiver1_email = request.form['receiver1_email']
        receiver2_email = request.form['receiver2_email']
        '''
        cursor.execute("SELECT * FROM NOTIFICATION")
        rows = cursor.fetchall()
        for row in rows:
           print(row)
		'''
        # Check if a SubjectCode with the same SubjectCode already exists
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM NOTIFICATION WHERE NotiCode = ?", noti_code)
        row = cursor.fetchone()
        
        if row:
            # A subject with the same section_code already exists
            message = 'A notification with NotiCode ' + noti_code + ' already exists.'
            return render_template('notification_message.html', message=message)
        else:
            # No notification with the same NotiCode exists, so insert the new section
            cursor.execute("INSERT INTO NOTIFICATION (NotiCode,NotiDate,NotiSender,NotiReceiver1,NotiReceiver2,NotiSubject,Campus,SenderEmail,Receiver1Email,Receiver2Email,CreatedBy,CreatedOn,UpdatedBy,UpdatedOn) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
              noti_code,noti_date,noti_sender,noti_receiver1,noti_receiver2,noti_subject,campus,sender_email,receiver1_email,receiver2_email,user_id,xnow,user_id,xnow)
            conn.commit()

            message = 'New notification code ' + noti_code + ' added successfully.'
            return render_template('notification_message.html', message=message)

    # If the request method is GET, show the add notification form
    return render_template('notification_add.html')

@app.route('/delete_notification', methods=['GET', 'POST'])	
def delete_notification():
    global user_id
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()
    if not user.CanDeleteNotification:
        message = 'You are not allowed to run DELETE NOTIFICATION. Please see the Administrator.'
        return render_template('notification_message.html', message=message)
    if request.method == 'POST':
        # Get the campus info from the form
        noti_code = request.form['noti_code']
		
		# Check if campus exists
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM NOTIFICATION WHERE NotiCode='{noti_code}'")
        existing_notification = cursor.fetchone()
        if existing_notification:
            sql = f"DELETE FROM NOTIFICATION WHERE NotiCode='{noti_code}'"
            cursor.execute(sql)
            conn.commit()
            message = 'Notification ' + noti_code + ' successfully deleted.'
            return render_template('notification_message.html', message=message)
        else:
            message = 'Notification code ' + noti_code + ' does not exist.'
            return render_template('notification_message.html', message=message)
    return render_template('notification_delete.html')
	
@app.route('/update_notification1', methods=['GET', 'POST'])
def update_notification1():
    global user_id
    global xnow
    cursor = conn.cursor()
    return render_template('update_notification1.html')
	
@app.route('/update_notification2', methods=['GET', 'POST'])	
def update_notification2():
    if request.method == 'POST':
        # Get the notification info from the  update_notification1 form
        noti_code = request.form['noti_code']
    
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')	
    cursor = conn.cursor()
 
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    cursor = conn.cursor()
	
    cursor.execute("SELECT * FROM NOTIFICATION WHERE NotiCode = ?", noti_code)
    notification = cursor.fetchone()

    return render_template('update_notification2.html',notification=notification)

@app.route('/update_notification', methods=['GET', 'POST'])
def update_notification():
    global user_id
    global xnow
    cursor = conn.cursor()
		
    if request.method == 'POST':
        # Get the notification info from the form
        noti_code = request.form['noti_code']
        noti_date = request.form['noti_date']
        noti_sender = request.form['noti_sender']
        noti_receiver1 = request.form['noti_receiver1']
        noti_receiver2 = request.form['noti_receiver2']
        noti_subject = request.form['noti_subject']
        campus = request.form['campus']
        sender_email = request.form['sender_email']
        receiver1_email = request.form['receiver1_email']
        receiver2_email = request.form['receiver2_email']
        '''
        cursor.execute("SELECT * FROM NOTIFICATION")
        rows = cursor.fetchall()
        for row in rows:
           print(row)
		'''
        # Check if a subject the same SubjectCode already exists
		
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM NOTIFICATION WHERE NotiCode = ?", noti_code)
        existing_notification = cursor.fetchone()
        notification = existing_notification
		
        if existing_notification:
            update_query = "UPDATE NOTIFICATION SET NotiDate=?,NotiSender=?,NotiReceiver1=?,NotiReceiver2=?,NotiSubject=?,Campus=?,SenderEmail=?,Receiver1Email=?,Receiver2Email=?,CreatedBy=?,CreatedOn=?,UpdatedBy=?,UpdatedOn=? WHERE NotiCode=?"
            cursor.execute(update_query, (noti_date,noti_sender,noti_receiver1,noti_receiver2,noti_subject,campus,sender_email,receiver1_email,receiver2_email,user_id,xnow,user_id,xnow,noti_code,))
            conn.commit()
            message = 'Notification code ' + noti_code + ' successfully updated..'
            return render_template('notification_message.html', message=message)
        else:
            message = 'Notification code ' + campus_code + ' does not exist.'
            return render_template('notification_message.html', message=message)
        
    # If the request method is GET, show the add notification form
    return render_template('update_notification1.html')
	
@app.route('/query_notification', methods=['GET', 'POST'])
def query_notification():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()
    if not user.CanQueryNotification:
        message = 'You are not allowed to run QUERY NOTIFICATION. Please see the Administrator.'
        return render_template('notification_message.html', message=message)
    if request.method == 'POST':
        noti_code = request.form['noti_code']
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM NOTIFICATION WHERE NotiCode='{noti_code}'")
        existing_notification = cursor.fetchone()
        if existing_notification:
            notification=existing_notification
            return render_template('notification.html', notification=existing_notification)
        else:
           message = 'Notification code ' + noti_code + ' does not exist.'
           return render_template('notification_message.html', message=message)
    return render_template('notification_query.html')
	
@app.route('/display_notifications/')
def display_notifications():
   # Set up connection to SQL Server database
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()

    if not user.CanDisplayNotification:
        message = 'You are not allowed to run DISPLAY NOTIFICATIONS. Please see the Administrator.'
        return render_template('notification_message.html', message=message)
    else:
        exec(open('display_notifications.py').read())
        return '-DISPLAY NOTIFICATIONS got clicked-'
	
# PARENT MENU
@app.route('/')  
@app.route('/parent_menu/')
#@app.route('/parent_menu/', endpoint='parent_menu')
def parent_menu():
    global user_id
    return render_template('parent_menu.html', user_id=user_id)
	
@app.route('/add_parent', methods=['GET', 'POST'])
def add_parent():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()
    if not user.CanAddParent:
        message = 'You are not allowed to run ADD PARENT. Please see the Administrator.'
        return render_template('message_parent.html', message=message)
		
    if request.method == 'POST':
        # Get the parent info from the form
        parent_id = request.form['parent_id']
        parent_name = request.form['parent_name']
        parent_type = request.form['parent_type']
        campus = request.form['campus']
        contact_number = request.form['contact_number']
        landline_number = request.form['landline_number']
        home_address = request.form['home_address']
        email_address = request.form['email_address']

        '''
        cursor.execute("SELECT * FROM PARENT")
        rows = cursor.fetchall()
        for row in rows:
           print(row)
		'''
        # Check if a parent with the same ParentID already exists
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM PARENT WHERE ParentID = ?", parent_id)
        row = cursor.fetchone()
        if row:
            # A parent with the same ParentID already exists
            message = 'A parent with ParentID ' + parent_id + ' already exists.'
            return render_template('message_parent.html', message=message)
        else:
            # No parent with the same ParentID exists, so insert the new parent
            cursor.execute("INSERT INTO PARENT (ParentID,ParentName,ParentType,Campus,ContactNumber,LandlineNumber,HomeAddress,EmailAddress,CreatedBy,CreatedOn,UpdatedBy,UpdatedOn) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
			parent_id,parent_name,parent_type,campus,contact_number,landline_number,home_address,email_address,'Vin',xnow,'Vin',xnow)
            conn.commit()

            message = 'New Parent ID ' + parent_id + ' added successfully.'
            return render_template('message_parent.html', message=message)

            return message
 
    # If the request method is GET, show the add parent form
    return render_template('add_parent.html')

@app.route('/delete_parent', methods=['GET', 'POST'])	
def delete_parent():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()
    if not user.CanDeleteParent:
        message = 'You are not allowed to run DELETE PARENT. Please see the Administrator.'
        return render_template('message_parent.html', message=message)

    if request.method == 'POST':
        # Get the parent info from the form
        parent_id = request.form['parent_id']
		
		# Check if parent exists
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM PARENT WHERE ParentID='{parent_id}'")
        existing_parent = cursor.fetchone()
        if existing_parent:
            sql = f"DELETE FROM PARENT WHERE ParentID='{parent_id}'"
            cursor.execute(sql)
            conn.commit()
            #return 'Parent ' + parent_id + ' successfully deleted.'
            message = 'Parent ID ' + parent_id + ' successfully deleted.'
            return render_template('message_parent.html', message=message)
        else:
            message = 'Parent ID ' + parent_id + ' does not exist.'
            return render_template('message_parent.html', message=message)
    return render_template('delete_parent.html')
	
@app.route('/update_parent1', methods=['GET', 'POST'])
def update_parent1():
    global user_id
    global xnow
    cursor = conn.cursor()
    return render_template('update_parent1.html')
	
@app.route('/update_parent2', methods=['GET', 'POST'])	
def update_parent2():
    if request.method == 'POST':

        parent_id = request.form['parent_id']
    
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')	
    cursor = conn.cursor()
    
    # Define the SELECT statement
    select_query2 = 'SELECT CampusCode,CampusName FROM CAMPUS'
    
    # Execute the query and fetch the results
    cursor.execute(select_query2)
    campuses = [(row[0], row[1]) for row in cursor.fetchall()]
    #print(campuses)   #successful
    
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    cursor = conn.cursor()
	
    cursor.execute("SELECT * FROM PARENT WHERE ParentID = ?", parent_id)
    parent = cursor.fetchone()

    return render_template('update_parent2.html',parent=parent,campuses=campuses)

@app.route('/update_parent', methods=['GET', 'POST'])
def update_parent():
    global user_id
    global xnow
    cursor = conn.cursor()
		
    if request.method == 'POST':
        # Get the subject info from the form
        parent_id = request.form['parent_id']
        parent_name = request.form['parent_name']
        contact_number = request.form['contact_number']
        landline_number = request.form['landline_number']
        home_address = request.form['home_address']
        campus = request.form['campus']
        email_address = request.form['email_address']
        parent_type = request.form['parent_type']
        '''
        cursor.execute("SELECT * FROM PARENT")
        rows = cursor.fetchall()
        for row in rows:
           print(row)
		'''
        # Check if a club with the same ClubCode already exists
		
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM PARENT WHERE ParentID = ?", parent_id)
        existing_parent = cursor.fetchone()
        parent = existing_parent

        if existing_parent:
            update_query = "UPDATE PARENT SET ParentName=?,ContactNumber=?,LandlineNumber=?,HomeAddress=?,ParentType=?,Campus=?,EmailAddress=?,CreatedBy=?,CreatedOn=?,UpdatedBy=?,UpdatedOn=? WHERE ParentID=?"
            cursor.execute(update_query, (parent_name,contact_number,landline_number,home_address,parent_type,campus,email_address,user_id,xnow,user_id,xnow,parent_id,))
            conn.commit()
            message = 'ParentID ' + parent_id + ' successfully updated..'
            return render_template('message_parent.html', message=message)
        else:
            message = 'ParentID ' + parent_id + ' does not exist.'
            return render_template('message_parent.html', message=message)
        
    # If the request method is GET, show the add club form
    return render_template('update_parent1.html')
	
@app.route('/query_parent', methods=['GET', 'POST'])
def query_parent():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()
    if not user.CanQueryParent:
        message = 'You are not allowed to run QUERY PARENT. Please see the Administrator.'
        return render_template('message_parent.html', message=message)
    if request.method == 'POST':
        parent_id = request.form['parent_id']
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM PARENT WHERE ParentID='{parent_id}'")
        existing_parent = cursor.fetchone()
        #print(existing_parent)
        if existing_parent:
            parent=existing_parent			
            return render_template('parent.html', parent=existing_parent)
        else:
           message = 'Parent ID ' + parent_id + ' does not exist.'
           return render_template('message_parent.html', message=message)
    return render_template('query_parent.html')
	
@app.route('/display_parents/')
def display_parents():
    # Set up connection to SQL Server database
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()

    if not user.CanDisplayParent:
        message = 'You are not allowed to run DISPLAY PARENTS. Please see the Administrator.'
        return render_template('message_parent.html', message=message)
    else:
        exec(open('display_parents.py').read())
        return '-DISPLAY PARENT got clicked-'	
  
# CLUB MENU
@app.route('/')
@app.route('/club_menu/')
def club_menu():
    global user_id
    return render_template('club_menu.html')
	
@app.route('/add_club', methods=['GET', 'POST'])
def add_club():
    global user_id
    global xnow
    #print(user_id)
	# Check if the user has permission to access this route
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()
	
    if not user.CanAddClub:
        message = 'You are not allowed to run ADD CLUB. Please see the Administrator.'
        return render_template('club_message.html', message=message)
		
    select_query2 = 'SELECT CampusName FROM CAMPUS'
    cursor.execute(select_query2)
    campuses = [row[0] for row in cursor.fetchall()]
	
    if request.method == 'POST':
        # Get the grade level info from the form
        clubcode = request.form['clubcode']
        clubname = request.form['clubname']
        adviser = request.form['adviser']
        maxmembers = request.form['maxmembers']
        campus = request.form['campus']
        no_of_members = request.form['no_of_members']
        '''
        cursor.execute("SELECT * FROM CLUB")
        rows = cursor.fetchall()
        for row in rows:
           print(row)
		'''
        # Check if a club with the same CLUB already exists
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM CLUB WHERE ClubCode = ?", clubcode)
        row = cursor.fetchone()
        if row:
            # A clubcode with the same ClubCode already exists
            message = 'A club with Club Code ' + clubcode + ' already exists.'
            return render_template('message_club.html', message=message)
        else:
            # No club with the same Club Code exists, so insert the new clubcode
            cursor.execute("INSERT INTO CLUB (ClubCode,ClubName,Adviser,MaxMembers,Campus,ActualNoOfMembers,CreatedBy,CreatedOn,UpdatedBy,UpdatedOn) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
              clubcode,clubname,adviser,maxmembers,campus,no_of_members,user_id,xnow,user_id,xnow)
            conn.commit()

            message = 'New Club ' + clubcode + ' added successfully.'
            return render_template('message_club.html', message=message)
			
            return message
 
    # If the request method is GET, show the add grade level form
    return render_template('add_club.html',campuses=campuses)

@app.route('/delete_club', methods=['GET', 'POST'])	
def delete_club():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()
	
    if not user.CanDeleteClub:
        message = 'You are not allowed to run DELETE CLUB. Please see the Administrator.'
        return render_template('club_message.html', message=message)
    if request.method == 'POST':
        # Get the grade level info from the form
        clubcode = request.form['clubcode']
		
		# Check if club exists
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM CLUB WHERE ClubCode='{clubcode}'")
        existing_club = cursor.fetchone()
        if existing_club:
            sql = f"DELETE FROM CLUB WHERE ClubCode='{clubcode}'"
            cursor.execute(sql)
            conn.commit()
            #return 'Grade Level ' + grade_level + ' successfully deleted.'
            message = 'Club Code ' + clubcode + ' successfully deleted.'
            return render_template('message_club.html', message=message)
        else:
            message = 'Club Code ' + clubcode + ' does not exist.'
            return render_template('message_club.html', message=message)
    return render_template('delete_club.html')
	
@app.route('/update_club1', methods=['GET', 'POST'])
def update_club1():
    global user_id
    global xnow
    cursor = conn.cursor()
    return render_template('update_club1.html')
	
@app.route('/update_club2', methods=['GET', 'POST'])	
def update_club2():
    if request.method == 'POST':
        # Get the subject info from the  update_subject1 form
        club_code = request.form['club_code']
    
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')	
    cursor = conn.cursor()
    
    # Define the SELECT statement
    select_query2 = 'SELECT CampusCode,CampusName FROM CAMPUS'
    
    # Execute the query and fetch the results
    cursor.execute(select_query2)
    campuses = [(row[0], row[1]) for row in cursor.fetchall()]
    #print(campuses)   #successful
    
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    cursor = conn.cursor()
	
    cursor.execute("SELECT * FROM CLUB WHERE ClubCode = ?", club_code)
    club = cursor.fetchone()

    return render_template('update_club2.html',club=club,campuses=campuses)

@app.route('/update_club', methods=['GET', 'POST'])
def update_club():
    global user_id
    global xnow
    cursor = conn.cursor()
		
    if request.method == 'POST':
        # Get the subject info from the form
        club_code = request.form['club_code']
        club_name = request.form['club_name']
        adviser = request.form['adviser']
        max_members = request.form['max_members']
        actual_no_of_members = request.form['actual_no_of_members']
        campus = request.form['campus']
        '''
        cursor.execute("SELECT * FROM CLUB")
        rows = cursor.fetchall()
        for row in rows:
           print(row)
		'''
        # Check if a club with the same ClubCode already exists
		
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM CLUB WHERE ClubCode = ?", club_code)
        existing_club = cursor.fetchone()
        club = existing_club
		
        if existing_club:
            update_query = "UPDATE CLUB SET ClubName=?,Adviser=?,MaxMembers=?,Campus=?,ActualNoOfMembers=?,CreatedBy=?,CreatedOn=?,UpdatedBy=?,UpdatedOn=? WHERE ClubCode=?"
            cursor.execute(update_query, (club_name,adviser,max_members,campus,actual_no_of_members,user_id,xnow,user_id,xnow,club_code,))
            conn.commit()
            message = 'Club code ' + club_code + ' successfully updated..'
            return render_template('club_message.html', message=message)
        else:
            message = 'Club code ' + club_code + ' does not exist.'
            return render_template('club_message.html', message=message)
        
    # If the request method is GET, show the add club form
    return render_template('update_club1.html')
	
@app.route('/query_club', methods=['GET', 'POST'])
def query_club():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()
	
    if not user.CanQueryClub:
        message = 'You are not allowed to run QUERY CLUB. Please see the Administrator.'
        return render_template('club_message.html', message=message)
    
    if request.method == 'POST':
        clubcode = request.form['clubcode']
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM CLUB WHERE ClubCode='{clubcode}'")
        existing_clubcode = cursor.fetchone()

        if existing_clubcode:
            club=existing_clubcode			
            return render_template('club.html', club=existing_clubcode)
        else:
           message = 'Club ' + clubcode + ' does not exist.'
           return render_template('message_club.html', message=message)
    return render_template('query_club.html')
	
@app.route('/display_club/')
def display_club():
    # Set up connection to SQL Server database
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()

    if not user.CanDisplayClub:
        message = 'You are not allowed to run DISPLAY CLUBS. Please see the Administrator.'
        return render_template('club_message.html', message=message)
    else:
        exec(open('display_clubs.py').read())
        return '-DISPLAY CLUBS got clicked-'
		
		
#USER MENU
@app.route('/') 
@app.route('/user_menu/')
def user_menu():
    global user_id
    try:
        #print(f'Request headers: {request.headers}')
        #print(f'Request data: {request.data}')
        # ... route code here

        return render_template('user_menu.html')
    except Exception as e:
        print(f'Error: {e}')
        raise
@app.route('/add_user', methods=['GET', 'POST'])
#@app.route('/add_user', methods=["POST"])
def add_user():
    global user_id
    global xnow
    #print('request.method = ' + request.method)
    #print('user_id = ' + user_id)  #  successful
    # Set up connection to SQL Server database
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
 	
	

    if request.method == 'POST':	# Capture field values from the Add User Form the save to database table LOGIN
	    # Get the field values from the form
        usercode = request.form['user_code']
        #print('POST usercode = ' + usercode)
        username = request.form['user_name']
        usertype = request.form['user_type']
        password = request.form['password']
        campus = request.form['campus']

        can_add_user = request.form.get('Can_Add_User') == 'on'
        can_delete_user = request.form.get('Can_Delete_User') == 'on'
        can_update_user = request.form.get('Can_Update_User') == 'on'
        can_query_user = request.form.get('Can_Query_User') == 'on'
        can_display_user = request.form.get('Can_Display_User') == 'on'

        can_add_student = request.form.get('Can_Add_Student') == 'on'
        can_delete_student = request.form.get('Can_Delete_Student') == 'on'
        can_update_student = request.form.get('Can_Update_Student') == 'on'
        can_query_student = request.form.get('Can_Query_Student') == 'on'
        can_display_student = request.form.get('Can_Display_Student') == 'on'

        can_add_teacher = request.form.get('Can_Add_Teacher') == 'on'
        can_delete_teacher = request.form.get('Can_Delete_Teacher') == 'on'
        can_update_teacher = request.form.get('Can_Update_Teacher') == 'on'
        can_query_teacher = request.form.get('Can_Query_Teacher') == 'on'
        can_display_teacher = request.form.get('Can_Display_Teacher') == 'on'
		
        can_add_parent = request.form.get('Can_Add_Parent') == 'on'
        can_delete_parent = request.form.get('Can_Delete_Parent') == 'on'
        can_update_parent = request.form.get('Can_Update_Parent') == 'on'
        can_query_parent = request.form.get('Can_Query_Parent') == 'on'
        can_display_parent = request.form.get('Can_Display_Parent') == 'on'
		
        can_add_admin = request.form.get('Can_Add_Admin') == 'on'
        can_delete_admin = request.form.get('Can_Delete_Admin') == 'on'
        can_update_admin = request.form.get('Can_Update_Admin') == 'on'
        can_query_admin = request.form.get('Can_Query_Admin') == 'on'
        can_display_admin = request.form.get('Can_Display_Admin') == 'on'
		
        can_add_section = request.form.get('Can_Add_Section') == 'on'
        can_delete_section = request.form.get('Can_Delete_Section') == 'on'
        can_update_section = request.form.get('Can_Update_Section') == 'on'
        can_query_section = request.form.get('Can_Query_Section') == 'on'
        can_display_section = request.form.get('Can_Display_Section') == 'on'
		
        can_add_subject = request.form.get('Can_Add_Subject') == 'on'
        can_delete_subject = request.form.get('Can_Delete_Subject') == 'on'
        can_update_subject = request.form.get('Can_Update_Subject') == 'on'
        can_query_subject = request.form.get('Can_Query_Subject') == 'on'
        can_display_subject = request.form.get('Can_Display_Subject') == 'on'
		
        can_add_club = request.form.get('Can_Add_Club') == 'on'
        can_delete_club = request.form.get('Can_Delete_Club') == 'on'
        can_update_club = request.form.get('Can_Update_Club') == 'on'
        can_query_club = request.form.get('Can_Query_Club') == 'on'
        can_display_club = request.form.get('Can_Display_Club') == 'on'
		
        can_add_clubmembers = request.form.get('Can_Add_ClubMembers') == 'on'
        can_delete_clubmembers = request.form.get('Can_Delete_ClubMembers') == 'on'
        can_update_clubmembers = request.form.get('Can_Update_ClubMembers') == 'on'
        can_query_clubmembers = request.form.get('Can_Query_ClubMembers') == 'on'
        can_display_clubmembers = request.form.get('Can_Display_ClubMembers') == 'on'
		
        can_add_campus = request.form.get('Can_Add_Campus') == 'on'
        can_delete_campus = request.form.get('Can_Delete_Campus') == 'on'
        can_update_campus = request.form.get('Can_Update_Campus') == 'on'
        can_query_campus = request.form.get('Can_Query_Campus') == 'on'
        can_display_campus = request.form.get('Can_Display_Campus') == 'on'
		
        can_add_quiz = request.form.get('Can_Add_Quiz') == 'on'
        can_delete_quiz = request.form.get('Can_Delete_Quiz') == 'on'
        can_update_quiz = request.form.get('Can_Update_Quiz') == 'on'
        can_query_quiz = request.form.get('Can_Query_Quiz') == 'on'
        can_display_quiz = request.form.get('Can_Display_Quiz') == 'on'
		
        can_add_formative = request.form.get('Can_Add_Formative') == 'on'
        can_delete_formative = request.form.get('Can_Delete_Formative') == 'on'
        can_update_formative = request.form.get('Can_Update_Formative') == 'on'
        can_query_formative = request.form.get('Can_Query_Formative') == 'on'
        can_display_formative = request.form.get('Can_Display_Formative') == 'on'
		
        can_add_alternative = request.form.get('Can_Add_Alternative') == 'on'
        can_delete_alternative = request.form.get('Can_Delete_Alternative') == 'on'
        can_update_alternative = request.form.get('Can_Update_Alternative') == 'on'
        can_query_alternative = request.form.get('Can_Query_Alternative') == 'on'
        can_display_alternative = request.form.get('Can_Display_Alternative') == 'on'
		
        can_add_perio = request.form.get('Can_Add_Perio') == 'on'
        can_delete_perio = request.form.get('Can_Delete_Perio') == 'on'
        can_update_perio = request.form.get('Can_Update_Perio') == 'on'
        can_query_perio = request.form.get('Can_Query_Perio') == 'on'
        can_display_perio = request.form.get('Can_Display_Perio') == 'on'
		
        can_add_bonus = request.form.get('Can_Add_Bonus') == 'on'
        can_delete_bonus = request.form.get('Can_Delete_Bonus') == 'on'
        can_update_bonus = request.form.get('Can_Update_Bonus') == 'on'
        can_query_bonus = request.form.get('Can_Query_Bonus') == 'on'
        can_display_bonus = request.form.get('Can_Display_Bonus') == 'on'
		
        can_add_notification = request.form.get('Can_Add_Notification') == 'on'
        can_delete_notification = request.form.get('Can_Delete_Notification') == 'on'
        can_update_notification = request.form.get('Can_Update_Notification') == 'on'
        can_query_notification = request.form.get('Can_Query_Notification') == 'on'
        can_display_notification = request.form.get('Can_Display_Notification') == 'on'
		
        can_view_gradecomp = request.form.get('Can_View_GradeComp') == 'on'
        can_view_reportcard = request.form.get('Can_View_ReportCard') == 'on'
        can_view_summscores = request.form.get('Can_View_SummScores') == 'on'
        can_view_directorlisters = request.form.get('Can_View_DirectorListers') == 'on'
        can_upload_data_from_excel = request.form.get('Can_Upload_Data_From_Excel') == 'on'

        # Check if a user with the same UserCode already exists
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM LOGIN WHERE UserCode = ?", usercode)
        row = cursor.fetchone()
        if row:
            # A usercode with the same User Code already exists
            message = 'A user with User Code ' + usercode + ' already exists.'
            return render_template('message_user.html', message=message)

        else:
            # No usercode with the same User Code exists, so insert the new clubcode
            insert_query = """ 
            INSERT INTO LOGIN (UserCode,UserName,UserType,Password,Campus,
			CanAddUser,CanDeleteUser,CanUpdateUser,CanQueryUser,CanDisplayUser,
            CanAddStudent,CanDeleteStudent,CanUpdateStudent,CanQueryStudent,CanDisplayStudent,
            CanAddTeacher,CanDeleteTeacher,CanUpdateTeacher,CanQueryTeacher,CanDisplayTeacher,
            CanAddParent,CanDeleteParent,CanUpdateParent,CanQueryParent,CanDisplayParent,
            CanAddAdmin,CanDeleteAdmin,CanUpdateAdmin,CanQueryAdmin,CanDisplayAdmin,
			CanAddSection,CanDeleteSection,CanUpdateSection,CanQuerySection,CanDisplaySection,
            CanAddSubject,CanDeleteSubject,CanUpdateSubject,CanQuerySubject,CanDisplaySubject,
            CanAddClub,CanDeleteClub,CanUpdateClub,CanQueryClub,CanDisplayClub,
            CanAddClubMembers,CanDeleteClubMembers,CanUpdateClubMembers,CanQueryClubMembers,CanDisplayClubMembers,
            CanAddCampus,CanDeleteCampus,CanUpdateCampus,CanQueryCampus,CanDisplayCampus,
            CanAddQuiz,CanDeleteQuiz,CanUpdateQuiz,CanQueryQuiz,CanDisplayQuiz,
            CanAddFormative,CanDeleteFormative,CanUpdateFormative,CanQueryFormative,CanDisplayFormative,
            CanAddAlternative,CanDeleteAlternative,CanUpdateAlternative,CanQueryAlternative,CanDisplayAlternative,
            CanAddPerio,CanDeletePerio,CanUpdatePerio,CanQueryPerio,CanDisplayPerio,
            CanAddBonus,CanDeleteBonus,CanUpdateBonus,CanQueryBonus,CanDisplayBonus,
            CanAddNotification,CanDeleteNotification,CanUpdateNotification,CanQueryNotification,CanDisplayNotification,
            CanViewSummScores,CanViewDirectorListers,CanViewGradeComp,CanViewReportCard,CanUploadDataFromExcel,
            CreatedBy,CreatedOn,UpdatedBy,UpdatedOn) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
			?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?)
            """
			
            values = (usercode,username,usertype,password,campus,
            can_add_user, can_delete_user, can_update_user, can_query_user, can_display_user,
            can_add_student, can_delete_student, can_update_student, can_query_student, can_display_student,
            can_add_teacher, can_delete_teacher, can_update_teacher, can_query_teacher, can_display_teacher,
            can_add_parent, can_delete_parent, can_update_parent, can_query_parent, can_display_parent,
            can_add_admin, can_delete_admin, can_update_admin, can_query_admin, can_display_admin,
			can_add_section, can_delete_section, can_update_section, can_query_section, can_display_section,
            can_add_subject, can_delete_subject, can_update_subject, can_query_subject, can_display_subject,
            can_add_club, can_delete_club, can_update_club, can_query_club, can_display_club,
            can_add_clubmembers, can_delete_clubmembers, can_update_clubmembers, can_query_clubmembers, can_display_clubmembers,
            can_add_campus, can_delete_campus, can_update_campus, can_query_campus, can_display_campus,
            can_add_quiz, can_delete_quiz, can_update_quiz, can_query_quiz, can_display_quiz,
            can_add_formative, can_delete_formative, can_update_formative, can_query_formative, can_display_formative,
            can_add_alternative, can_delete_alternative, can_update_alternative, can_query_alternative, can_display_alternative,
            can_add_perio, can_delete_perio, can_update_perio, can_query_perio, can_display_perio,
            can_add_bonus, can_delete_bonus, can_update_bonus, can_query_bonus, can_display_bonus,
            can_add_notification, can_delete_notification, can_update_notification, can_query_notification, can_display_notification,
            can_view_summscores, can_view_directorlisters, can_view_gradecomp, can_view_reportcard, can_upload_data_from_excel,
            user_id,xnow,user_id,xnow)
			
            cursor.execute(insert_query, values)

            conn.commit()

            message = 'New User ' + usercode + ' added successfully.'
            return render_template('message_user.html', message=message)
    else:
        # Define the SELECT statement
        select_query2 = 'SELECT CampusName FROM CAMPUS'
	
        # Execute the query and fetch the results
        cursor = conn.cursor()
        cursor.execute(select_query2)
        campuses = [row[0] for row in cursor.fetchall()]
	
        # Check if the user has permission to access this route
        cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
        user = cursor.fetchone()
        #print(user)  # executed succesfully
        if not user.CanAddUser:
            message = 'You are not allowed to ADD USER. Please see the Administrator.'
            return render_template('user_message.html', message=message)

 
    # If the request method is GET, show the add user form
    return render_template('add_user.html',campuses=campuses)     # To render Add User Form

@app.route('/delete_user', methods=['GET', 'POST'])	
def delete_user():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()
	
    if not user.CanDeleteUser:
        message = 'You are not allowed to run DELETE SYSTEM USER. Please see the Administrator.'
        return render_template('message_user.html', message=message)
    if request.method == 'POST':
        # Get the userinfo from the form
        usercode = request.form['usercode']
		
		# Check if user exists
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM LOGIN WHERE UserCode='{usercode}'")
        existing_user = cursor.fetchone()
        if existing_user:
            sql = f"DELETE FROM LOGIN WHERE UserCode='{usercode}'"
            cursor.execute(sql)
            conn.commit()
            #return 'User' + usercode + ' successfully deleted.'
            message = 'User Code ' + usercode + ' successfully deleted.'
            return render_template('message_user.html', message=message)
        else:
            message = 'User Code ' + usercode + ' does not exist.'
            return render_template('user_message.html', message=message)
    return render_template('delete_user.html')
	
@app.route('/update_user1', methods=['GET', 'POST'])
def update_user1():
    global user_id
    global xnow
    cursor = conn.cursor()
	# Check if the user has permission to access this route
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()

    if not user.CanUpdateUser:
        message = 'You are not allowed to run UPDATE USER. Please see the Administrator.'
        return render_template('user_message.html', message=message)
    return render_template('update_user1.html') 	# Render blank  form  to accept user input for usercode
	
@app.route('/update_user2', methods=['GET', 'POST'])	
def update_user2():
    #print('request.method = ' + request.method)
    if request.method == 'POST':	# request.method = POST
        # Get the student info from the  update_student1 form
        usercode = request.form['usercode']
        #print(usercode)		# usercode = DM
    cursor = conn.cursor()
	
	# Define the SELECT statement
    select_query2 = 'SELECT CampusName FROM CAMPUS'
	
	# Execute the query and fetch the results
    cursor.execute(select_query2)
    campuses = [row[0] for row in cursor.fetchall()]
	
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode = ?", usercode)
    user = cursor.fetchone()
    #print(user)  # successful, user has values
    return render_template('update_user2.html',campuses=campuses,user=user)
	
@app.route('/update_user', methods=['GET', 'POST'])
def update_user():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()

    if not user.CanUpdateUser:
        message = 'You are not allowed to run UPDATE SYSTEM USER. Please see the Administrator.'
        return render_template('user_message.html', message=message)
    if request.method == 'POST':
	    # Get the field values from the form
        usercode = request.form['user_code']
        #print('POST usercode = ' + usercode)
        username = request.form['user_name']
        usertype = request.form['user_type']
        campus = request.form['campus']
        password = request.form['password']

        can_add_user = request.form.get('Can_Add_User') == 'on'
        can_delete_user = request.form.get('Can_Delete_User') == 'on'
        can_update_user = request.form.get('Can_Update_User') == 'on'
        can_query_user = request.form.get('Can_Query_User') == 'on'
        can_display_user = request.form.get('Can_Display_User') == 'on'

        can_add_student = request.form.get('Can_Add_Student') == 'on'
        can_delete_student = request.form.get('Can_Delete_Student') == 'on'
        can_update_student = request.form.get('Can_Update_Student') == 'on'
        can_query_student = request.form.get('Can_Query_Student') == 'on'
        can_display_student = request.form.get('Can_Display_Student') == 'on'

        can_add_teacher = request.form.get('Can_Add_Teacher') == 'on'
        can_delete_teacher = request.form.get('Can_Delete_Teacher') == 'on'
        can_update_teacher = request.form.get('Can_Update_Teacher') == 'on'
        can_query_teacher = request.form.get('Can_Query_Teacher') == 'on'
        can_display_teacher = request.form.get('Can_Display_Teacher') == 'on'
		
        can_add_parent = request.form.get('Can_Add_Parent') == 'on'
        can_delete_parent = request.form.get('Can_Delete_Parent') == 'on'
        can_update_parent = request.form.get('Can_Update_Parent') == 'on'
        can_query_parent = request.form.get('Can_Query_Parent') == 'on'
        can_display_parent = request.form.get('Can_Display_Parent') == 'on'
		
        can_add_admin = request.form.get('Can_Add_Admin') == 'on'
        can_delete_admin = request.form.get('Can_Delete_Admin') == 'on'
        can_update_admin = request.form.get('Can_Update_Admin') == 'on'
        can_query_admin = request.form.get('Can_Query_Admin') == 'on'
        can_display_admin = request.form.get('Can_Display_Admin') == 'on'
		
        can_add_section = request.form.get('Can_Add_Section') == 'on'
        can_delete_section = request.form.get('Can_Delete_Section') == 'on'
        can_update_section = request.form.get('Can_Update_Section') == 'on'
        can_query_section = request.form.get('Can_Query_Section') == 'on'
        can_display_section = request.form.get('Can_Display_Section') == 'on'
		
        can_add_subject = request.form.get('Can_Add_Subject') == 'on'
        can_delete_subject = request.form.get('Can_Delete_Subject') == 'on'
        can_update_subject = request.form.get('Can_Update_Subject') == 'on'
        can_query_subject = request.form.get('Can_Query_Subject') == 'on'
        can_display_subject = request.form.get('Can_Display_Subject') == 'on'
		
        can_add_club = request.form.get('Can_Add_Club') == 'on'
        can_delete_club = request.form.get('Can_Delete_Club') == 'on'
        can_update_club = request.form.get('Can_Update_Club') == 'on'
        can_query_club = request.form.get('Can_Query_Club') == 'on'
        can_display_club = request.form.get('Can_Display_Club') == 'on'
		
        can_add_clubmembers = request.form.get('Can_Add_ClubMembers') == 'on'
        can_delete_clubmembers = request.form.get('Can_Delete_ClubMembers') == 'on'
        can_update_clubmembers = request.form.get('Can_Update_ClubMembers') == 'on'
        can_query_clubmembers = request.form.get('Can_Query_ClubMembers') == 'on'
        can_display_clubmembers = request.form.get('Can_Display_ClubMembers') == 'on'
		
        can_add_campus = request.form.get('Can_Add_Campus') == 'on'
        can_delete_campus = request.form.get('Can_Delete_Campus') == 'on'
        can_update_campus = request.form.get('Can_Update_Campus') == 'on'
        can_query_campus = request.form.get('Can_Query_Campus') == 'on'
        can_display_campus = request.form.get('Can_Display_Campus') == 'on'
		
        can_add_quiz = request.form.get('Can_Add_Quiz') == 'on'
        can_delete_quiz = request.form.get('Can_Delete_Quiz') == 'on'
        can_update_quiz = request.form.get('Can_Update_Quiz') == 'on'
        can_query_quiz = request.form.get('Can_Query_Quiz') == 'on'
        can_display_quiz = request.form.get('Can_Display_Quiz') == 'on'
		
        can_add_formative = request.form.get('Can_Add_Formative') == 'on'
        can_delete_formative = request.form.get('Can_Delete_Formative') == 'on'
        can_update_formative = request.form.get('Can_Update_Formative') == 'on'
        can_query_formative = request.form.get('Can_Query_Formative') == 'on'
        can_display_formative = request.form.get('Can_Display_Formative') == 'on'
		
        can_add_alternative = request.form.get('Can_Add_Alternative') == 'on'
        can_delete_alternative = request.form.get('Can_Delete_Alternative') == 'on'
        can_update_alternative = request.form.get('Can_Update_Alternative') == 'on'
        can_query_alternative = request.form.get('Can_Query_Alternative') == 'on'
        can_display_alternative = request.form.get('Can_Display_Alternative') == 'on'
		
        can_add_perio = request.form.get('Can_Add_Perio') == 'on'
        can_delete_perio = request.form.get('Can_Delete_Perio') == 'on'
        can_update_perio = request.form.get('Can_Update_Perio') == 'on'
        can_query_perio = request.form.get('Can_Query_Perio') == 'on'
        can_display_perio = request.form.get('Can_Display_Perio') == 'on'
		
        can_add_bonus = request.form.get('Can_Add_Bonus') == 'on'
        can_delete_bonus = request.form.get('Can_Delete_Bonus') == 'on'
        can_update_bonus = request.form.get('Can_Update_Bonus') == 'on'
        can_query_bonus = request.form.get('Can_Query_Bonus') == 'on'
        can_display_bonus = request.form.get('Can_Display_Bonus') == 'on'
		
        can_add_notification = request.form.get('Can_Add_Notification') == 'on'
        can_delete_notification = request.form.get('Can_Delete_Notification') == 'on'
        can_update_notification = request.form.get('Can_Update_Notification') == 'on'
        can_query_notification = request.form.get('Can_Query_Notification') == 'on'
        can_display_notification = request.form.get('Can_Display_Notification') == 'on'
		
        can_view_gradecomp = request.form.get('Can_View_GradeComp') == 'on'
        can_view_reportcard = request.form.get('Can_View_ReportCard') == 'on'
        can_view_summscores = request.form.get('Can_View_SummScores') == 'on'
        can_view_directorlisters = request.form.get('Can_View_DirectorListers') == 'on'
        can_upload_data_from_excel = request.form.get('Can_Upload_Data_From_Excel') == 'on'
        #print(can_add_quiz)    # getting the correct boolean value
        #print(can_display_quiz)     # getting the correct boolean value

        # Check if a user with the same UserCode already exists
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM LOGIN WHERE UserCode = ?", usercode)
        row = cursor.fetchone()
        if not row:
            message = 'A user with User Code ' + usercode + ' does not exist.'
            return render_template('message_user.html', message=message)

        # Check if a club with the sameClubCode already exists
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM LOGIN WHERE UserCode = ?", usercode)
        existing_usercode = cursor.fetchone()

        if existing_usercode:
            update_query = """
			UPDATE LOGIN SET UserName=?,UserType=?,Campus=?,Password=?,
            CanAddUser=?,CanDeleteUser=?,CanUpdateUser=?,CanQueryUser=?,CanDisplayUser=?,
            CanAddStudent=?,CanDeleteStudent=?,CanUpdateStudent=?,CanQueryStudent=?,CanDisplayStudent=?,
            CanAddTeacher=?,CanDeleteTeacher=?,CanUpdateTeacher=?,CanQueryTeacher=?,CanDisplayTeacher=?,
            CanAddParent=?,CanDeleteParent=?,CanUpdateParent=?,CanQueryParent=?,CanDisplayParent=?,
            CanAddAdmin=?,CanDeleteAdmin=?,CanUpdateAdmin=?,CanQueryAdmin=?,CanDisplayAdmin=?,
            CanAddSection=?,CanDeleteSection=?,CanUpdateSection=?,CanQuerySection=?,CanDisplaySection=?,
            CanAddSubject=?,CanDeleteSubject=?,CanUpdateSubject=?,CanQuerySubject=?,CanDisplaySubject=?,
            CanAddClub=?,CanDeleteClub=?,CanUpdateClub=?,CanQueryClub=?,CanDisplayClub=?,
            CanAddClubMembers=?,CanDeleteClubMembers=?,CanUpdateClubMembers=?,CanQueryClubMembers=?,CanDisplayClubMembers=?,
            CanAddCampus=?,CanDeleteCampus=?,CanUpdateCampus=?,CanQueryCampus=?,CanDisplayCampus=?,
            CanAddQuiz=?,CanDeleteQuiz=?,CanUpdateQuiz=?,CanQueryQuiz=?,CanDisplayQuiz=?,
            CanAddFormative=?,CanDeleteFormative=?,CanUpdateFormative=?,CanQueryFormative=?,CanDisplayFormative=?,
            CanAddAlternative=?,CanDeleteAlternative=?,CanUpdateAlternative=?,CanQueryAlternative=?,CanDisplayAlternative=?,
            CanAddPerio=?,CanDeletePerio=?,CanUpdatePerio=?,CanQueryPerio=?,CanDisplayPerio=?,
            CanAddBonus=?,CanDeleteBonus=?,CanUpdateBonus=?,CanQueryBonus=?,CanDisplayBonus=?,
            CanAddNotification=?,CanDeleteNotification=?,CanUpdateNotification=?,CanQueryNotification=?,CanDisplayNotification=?,
            CanViewSummScores=?, CanViewDirectorListers=?, CanViewGradeComp=?, CanViewReportCard=?, CanUploadDataFromExcel=?,
            CreatedBy=?,CreatedOn=?,UpdatedBy=?,UpdatedOn=? WHERE UserCode=?
			"""
			
            cursor.execute(update_query, (username,usertype,campus,password,
            can_add_user, can_delete_user, can_update_user, can_query_user, can_display_user,			
			can_add_student,can_delete_student,can_update_student,can_query_student,can_display_student,
			can_add_teacher,can_delete_teacher,can_update_teacher,can_query_teacher,can_display_teacher,
			can_add_parent,can_delete_parent,can_update_parent,can_query_parent,can_display_parent,
			can_add_admin,can_delete_admin,can_update_admin,can_query_admin,can_display_admin,
			can_add_section,can_delete_section,can_update_section,can_query_section,can_display_section,
			can_add_subject,can_delete_subject,can_update_subject,can_query_subject,can_display_subject,
			can_add_club,can_delete_club,can_update_club,can_query_club,can_display_club,
            can_add_clubmembers,can_delete_clubmembers,can_update_clubmembers,can_query_clubmembers,can_display_clubmembers,
			can_add_campus,can_delete_campus,can_update_campus,can_query_campus,can_display_campus,
			can_add_quiz,can_delete_quiz,can_update_quiz,can_query_quiz,can_display_quiz,
			can_add_formative,can_delete_formative,can_update_formative,can_query_formative,can_display_formative,
			can_add_alternative,can_delete_alternative,can_update_alternative,can_query_alternative,can_display_alternative,
			can_add_perio,can_delete_perio,can_update_perio,can_query_perio,can_display_perio,
			can_add_bonus,can_delete_bonus,can_update_bonus,can_query_bonus,can_display_bonus,
			can_add_notification,can_delete_notification,can_update_notification,can_query_notification,can_display_notification,
			can_view_summscores, can_view_directorlisters, can_view_gradecomp, can_view_reportcard, can_upload_data_from_excel,
			user_id,xnow,user_id,xnow,usercode,))
			
            conn.commit()
            message = 'User Code ' + usercode + ' successfully updated..'
            return render_template('message_user.html', message=message)
        else:
            message = 'User Code ' + usercode + ' does not exist.'
            return render_template('message_user.html', message=message)
        
    # If the request method is GET
    return render_template('update_user1.html')
	
@app.route('/query_user', methods=['GET', 'POST'])
def query_user():
    global user_id
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()
	
    if not user.CanQueryUser:
        message = 'You are not allowed to run QUERY USER. Please see the Administrator.'
        return render_template('message_user.html', message=message)
    #print('request.method = ' + request.method)
    if request.method == 'POST':
        usercode = request.form['usercode']
        usercode=usercode.strip()
        #print('usercode = ' + usercode)   # usercode = 20-120145-G
        cursor.execute(f"SELECT * FROM LOGIN WHERE UserCode='{usercode}'")
        existing_usercode = cursor.fetchone()

        if existing_usercode:
            usercode=existing_usercode			
            return render_template('user.html', usercode=usercode)
        else:
           message = 'User Code ' + usercode + ' does not exist.'
           return render_template('message_user.html', message=message)
    return render_template('query_user.html')   # Render blank form to accept user entry for usercode
	
@app.route('/display_user/')
def display_user():
    # Set up connection to SQL Server database
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()

    if not user.CanDisplayUser:
        message = 'You are not allowed to run DISPLAY USERS. Please see the Administrator.'
        return render_template('message_user.html', message=message)
    else:
        exec(open('display_user.py').read())
        return '-DISPLAY USERS got clicked-'
		
		
# QUIZ MENU
@app.route('/quiz_menu/')
def quiz_menu():
    global user_id
    return render_template('quiz_menu.html')
	
@app.route('/add_quiz', methods=['GET', 'POST'])
def add_quiz():
    global user_id
    global xnow
	
	# Set up connection to SQL Server database
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
	
    cursor = conn.cursor()
	
	# Define the SELECT statement
    select_query2 = 'SELECT StudentNumber,FirstName,FamilyName FROM STUDENT'
    select_query3 = 'SELECT SectionCode,SectionName FROM SECTION'
    select_query4 = 'SELECT SubjectCode,SubjectName FROM SUBJECT'
    select_query5 = 'SELECT CampusCode,CampusName FROM CAMPUS'
	
	# Execute the query and fetch the results
    cursor.execute("SELECT TeacherID,TeacherName FROM TEACHER WHERE TeacherID=?",user_id)
    teachers = [(row[0], row[1]) for row in cursor.fetchall()]
	
    cursor.execute(select_query2)
    students = [(row[0], row[1].strip(), row[2].strip()) for row in cursor.fetchall()]
 
    cursor.execute(select_query3)
    sections = [(row[0], row[1]) for row in cursor.fetchall()]
	
    cursor.execute(select_query4)
    subjects = [(row[0], row[1]) for row in cursor.fetchall()]
	
    cursor.execute(select_query5)
    campuses = [(row[0], row[1]) for row in cursor.fetchall()]
	
    # Check if the user has permission to access this route
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()
    #print(user)
    if not user.CanAddQuiz:
        message = 'You are not allowed to run ADD QUIZ. Please see the Administrator.'
        return render_template('quiz_message.html', message=message)
		
    if request.method == 'POST':
        # Get the quiz info from the form
        quizno = request.form['quizno']
        quizdate = request.form['quizdate']
        teachername = request.form['teachername']
        studentnumber = request.form['studentnumber']
        studentname = request.form['studentname']
        subjectname = request.form['subjectname']
        campusname = request.form['campusname']
        sectionname = request.form['sectionname']
        gradelevel = request.form['gradelevel']
        quarter = request.form['quarter']
        score = request.form['score']
        noofitems = request.form['noofitems']
        teacher_commentsfeedback = request.form['teacher_commentsfeedback']
        '''
        cursor.execute("SELECT * FROM QUIZ")
        rows = cursor.fetchall()
        for row in rows:
           print(row)
		'''
        # Set up connection to SQL Server database
        server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
        database = 'TransDB'
        username = 'sa'
        password = 'noabrir'
        driver = '{SQL Server}'

        conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
		
        # Check if a quiz with the same QuizNo already exists
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM QUIZ WHERE QuizNo = ?", quizno)
        row = cursor.fetchone()
        if row:
            # A quiz with the same Quiz No. already exists
            message = 'A quiz with Quiz No. ' + quizno + ' already exists.'
            return render_template('quiz_message.html', message=message)
        else:
            # No quizno with the same QuizNo exists, so insert the new quiz
            cursor.execute("INSERT INTO QUIZ (QuizNo,QuizDate,TeacherID, TeacherName,StudentNumber,StudentName,SubjectName,CampusName,SectionName,GradeLevel,Quarter,Score,NoOfItems,TeacherCommentsFeedback,CreatedBy,CreatedOn,UpdatedBy,UpdatedOn) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
              quizno,quizdate,user_id,teachername,studentnumber,studentname,subjectname,campusname,sectionname,gradelevel,quarter,score,noofitems,teacher_commentsfeedback,user_id,xnow,user_id,xnow)
            conn.commit()

            message = 'New Quiz No. ' + quizno + ' added successfully.'
            return render_template('quiz_message.html', message=message)
		
            return message
 
    # If the request method is GET, show the add quiz form
    return render_template('quiz_add.html',teachers=teachers,students=students,sections=sections,subjects=subjects,campuses=campuses)

@app.route('/delete_quiz', methods=['GET', 'POST'])	
def delete_quiz():
    global user_id
    global xnow
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
	# Check if the user has permission to access this route
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()

    if not user.CanDeleteQuiz:
        message = 'You are not allowed to run DELETE QUIZ. Please see the Administrator.'
        return render_template('quiz_message.html', message=message)
		
    if request.method == 'POST':
        # Get the quizinfo from the form
        quizno = request.form['quizno']
		
		# Check if quiz exists
        server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
        database = 'TransDB'
        username = 'sa'
        password = 'noabrir'
        driver = '{SQL Server}'

        conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
        cursor = conn.cursor()
		
        cursor.execute(f"SELECT * FROM QUIZ WHERE QuizNo='{quizno}'")
        existing_quiz = cursor.fetchone()
        if existing_quiz:
            sql = f"DELETE FROM QUIZ WHERE QuizNo='{quizno}'"
            cursor.execute(sql)
            conn.commit()
            #return 'Quiz' + quizno + ' successfully deleted.'
            message = 'Quiz ' + quizno + ' successfully deleted.'
            return render_template('quiz_message.html', message=message)
        else:
            message = 'Quiz No. ' + quizno + ' does not exist.'
            return render_template('quiz_message.html', message=message)
    return render_template('quiz_delete.html')
	
@app.route('/update_quiz1', methods=['GET', 'POST'])
def update_quiz1():
    global user_id
    global xnow
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    cursor = conn.cursor()
	# Check if the user has permission to access this route
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()
    #print(user)	# successful, user has row values
    if not user.CanUpdateQuiz:
        message = 'You are not allowed to run UPDATE QUIZ. Please see the Administrator.'
        return render_template('quiz_message.html', message=message)
    return render_template('update_quiz1.html')
	
@app.route('/update_quiz2', methods=['GET', 'POST'])	
def update_quiz2():
    if request.method == 'POST':
        # Get the quiz info from the  update_quiz1 form
        quizno = request.form['quizno']
    
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')	
    cursor = conn.cursor()
	
    # Define the SELECT statement
    select_query2 = 'SELECT StudentNumber,FirstName,FamilyName FROM STUDENT'
    select_query3 = 'SELECT SectionName FROM SECTION'
    select_query4 = 'SELECT SubjectName FROM SUBJECT'
    select_query5 = 'SELECT CampusName FROM CAMPUS'
	
	# Execute the query and fetch the results
    cursor.execute("SELECT * FROM TEACHER WHERE TeacherID=?", user_id)
    teachers = [(row[0], row[1]) for row in cursor.fetchall()]
	
    cursor.execute(select_query2)
    students = [(row[0], row[1], row[2]) for row in cursor.fetchall()]
 
    cursor.execute(select_query3)
    sections = [(row[0]) for row in cursor.fetchall()]
	
    cursor.execute(select_query4)
    subjects = [(row[0]) for row in cursor.fetchall()]
	
    cursor.execute(select_query5)
    campuses = [(row[0]) for row in cursor.fetchall()]
	
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'TransDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    cursor = conn.cursor()
	
    cursor.execute("SELECT * FROM QUIZ WHERE QuizNo = ?", quizno)
    quiz = cursor.fetchone()
    #print(quiz)
    #print(teachers)
    return render_template('update_quiz2.html',quiz=quiz,teachers=teachers,students=students,sections=sections,subjects=subjects,campuses=campuses)

@app.route('/update_quiz', methods=['GET', 'POST'])
def update_quiz():
    global user_id
    global xnow
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')	
    cursor = conn.cursor()

    # Check if the user has permission to access this route
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()
    #print(user)    # successful, user has values
    if not user.CanUpdateQuiz:
        message = 'You are not allowed to run UPDATE QUIZ. Please see the Administrator.'
        return render_template('quiz_message.html', message=message)
		
    if request.method == 'POST':
        # Get the quiz info from the form
        quizno = request.form['quizno']
        quizdate = request.form['quizdate']
        teacherid = request.form['teacherid']
        teachername = request.form['teachername']
        studentnumber = request.form['studentnumber']
        studentname = request.form['studentname']
        subjectname = request.form['subjectname']
        campusname = request.form['campusname']
        sectionname = request.form['sectionname']
        gradelevel = request.form['gradelevel']
        quarter = request.form['quarter']
        score = request.form['score']
        noofitems = request.form['noofitems']
        teacher_commentsfeedback = request.form['teacher_commentsfeedback']
        '''
        cursor.execute("SELECT * FROM STUDENT")
        rows = cursor.fetchall()
        for row in rows:
           print(row)
		'''
        # Check if a quiz with the same QuizNo already exists
        server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
        database = 'TransDB'
        username = 'sa'
        password = 'noabrir'
        driver = '{SQL Server}'

        conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')	
		
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM QUIZ WHERE QuizNo = ?", quizno)
        existing_quiz = cursor.fetchone()
        quiz = existing_quiz
		
        if existing_quiz:
            update_query = "UPDATE QUIZ SET QuizDate=?,TeacherID=?,TeacherName=?,StudentNumber=?,StudentName=?,SubjectName=?,CampusName=?,SectionName=?,GradeLevel=?,Score=?,NoOfItems=?,TeacherCommentsFeedback=?,CreatedBy=?,CreatedOn=?,UpdatedBy=?,UpdatedOn=? WHERE QuizNo=?"
            cursor.execute(update_query, (quizdate,teacherid,teachername,studentnumber,studentname,subjectname,campusname,sectionname,gradelevel,score,noofitems,teacher_commentsfeedback,user_id,xnow,user_id,xnow,quizno,))
            conn.commit()
            message = 'Quiz No. ' + quizno + ' successfully updated..'
            return render_template('quiz_message.html', message=message)
        else:
            message = 'Student number ' + student_number + ' does not exist.'
            return render_template('quiz_message.html', message=message)
        
    # If the request method is GET
    return render_template('update_quiz1.html')

	
@app.route('/query_quiz', methods=['GET', 'POST'])	
def query_quiz():
    global user_id
    global xnow
    #print (user_id)	# user_id=DM

    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    
    cursor = conn.cursor()
    cursor.execute("SELECT UserCode,UserType,CanQueryQuiz FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()
    xuser=user[0]
    print('user_id = ' + user_id) # 20-120145-P
    print('xuser = ' + xuser)   # 20-120145-P
    part1, part2, part3 = xuser.split("-")
    print('part1 = ' + part1)  # 20
    print('part2 = ' + part2)  # 120145
    print('part3 = ' + part3)  # P
    xuser = part1 + '-' + part2
    print('xuser = ' + xuser)
    user_type=user[1] 
    print('user_type = ' + user_type)  # Parent
    
    if not user.CanQueryQuiz:
        message = 'You are not allowed to run QUERY QUIZ. Please see the Administrator.'
        return render_template('quiz_message.html', message=message)
		
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'TransDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    cursor = conn.cursor()
	
    if request.method == 'POST':
        quizno = request.form['quizno']
        cursor.execute(f"SELECT * FROM QUIZ WHERE QuizNo='{quizno}' and StudentNumber='{xuser}'")
        existing_quiz = cursor.fetchone()

        if existing_quiz:
            quiz=existing_quiz
            xquiz=quiz.QuizDate
            year = xquiz.strftime("%Y")
            month = xquiz.strftime("%m")
            day = xquiz.strftime("%d")
            xquizdate=year + '-' + month + '-' + day
            quiz.QuizDate = xquizdate 
            quiz.StudentName=quiz.StudentName.upper()

            return render_template('quiz.html', quiz=existing_quiz)
        else:
           message = 'Quiz No. ' + quizno + ' does not exist or (the student is not yourself or is not your son/daughter/ward.)'
           return render_template('quiz_message.html', message=message)
    return render_template('quiz_query.html')
	

#@app.route('/index_quizzes')
@app.route('/index_quizzes', methods=['GET', 'POST'])	
def index_quizzes():
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    database_transdb = 'TransDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn_masterdb = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    cursor_masterdb = conn_masterdb.cursor()
    cursor_masterdb.execute("SELECT UserCode, UserType FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor_masterdb.fetchone()
    '''
    #print('1-user.UserType = ' + user.UserType)   # 1-user.UserType = Student
    user.UserType = user.UserType.strip()

    if user.UserType=='Student' or user.UserType=='Parent' or user.UserType=='Guardian' or user.UserType=='Admin':
        cursor_masterdb.execute("SELECT TeacherName FROM TEACHER")
        teachers = cursor_masterdb.fetchall()
        print('2-user.UserType = ' + user.UserType)    # 2-user.UserType = Student
        for teacher in teachers:
            print('2-TeacherName = ' + teacher[0])
    elif user.UserType=='Teacher':
        teachers = []
        cursor_masterdb.execute("SELECT TeacherName FROM TEACHER WHERE TeacherID=?", user_id)
        teacher = cursor_masterdb.fetchone()
        if teacher is not None:
            teacher_name = teacher
            print('3-TeacherName = ' + str(teacher_name))    # 3-TeacherName = ('DINNIE MORALES                                              ',)
            teachers.append(teacher_name)
        else:
            print('No teacher found with the given TeacherID')
	'''		
    # Fetch the students from the STUDENT table
    select_students_query = 'SELECT StudentNumber, FirstName, FamilyName FROM STUDENT'
    cursor_masterdb.execute(select_students_query)
    students = [(row[0], row[1].strip(), row[2].strip()) for row in cursor_masterdb.fetchall()]

    #Fetch the teachers from the TEACHER table
    cursor_masterdb.execute("SELECT TeacherName FROM TEACHER")   # WHERE TeacherID=?", user_id)
    cursor_masterdb.execute("SELECT TeacherName FROM TEACHER")
    teachers = cursor_masterdb.fetchall()

    # Fetch the sections from the SECTION table
    select_sections_query = 'SELECT SectionName FROM SECTION'
    cursor_masterdb.execute(select_sections_query)
    sections = cursor_masterdb.fetchall()

    # Fetch the subjects from the SUBJECT table
    select_subjects_query = 'SELECT SubjectName FROM SUBJECT'
    cursor_masterdb.execute(select_subjects_query)
    subjects = cursor_masterdb.fetchall()

    # Close the database connection
    #conn_masterdb.close()

    return render_template('index_quizzes.html', students=students, teachers=teachers, sections=sections, subjects=subjects)

	
@app.route('/query_quizzes', methods=['GET', 'POST'])	
def query_quizzes():
    global user_id
    global xnow
    #print (user_id)	# user_id=DM
    # Get the selected values from the form
    student_name = request.form['student_name']
    teacher_name = request.form['teacher_name']
    section_name = request.form['section_name']
    subject_name = request.form['subject_name']
    quarter_number = request.form['quarter_number']
    #print(student_name)   # Vincent II           Conti
    # Connect to the TransDB database
    database = 'TransDB'
    conn_transdb = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    cursor_transdb = conn_transdb.cursor()

    # Define the SELECT statement to fetch the quiz scores
    select_quizzes_query = '''
    SELECT QuizNo, Score, NoOfItems FROM QUIZ WHERE StudentName=? AND TeacherName=? AND SectionName=? AND SubjectName=? AND Quarter=?
    '''
	# Execute the query and fetch the results
    cursor_transdb.execute(select_quizzes_query, (student_name, teacher_name, section_name, subject_name, quarter_number))
    quizzes = cursor_transdb.fetchall()

    # Close the TransDB database connection
    conn_transdb.close()

    return render_template('query_quizzes.html', quizzes=quizzes, student_name=student_name, teacher_name=teacher_name, section_name=section_name, subject_name=subject_name, quarter_number=quarter_number)
	
@app.route('/display_quiz/')
def display_quiz():
    global user_id

    # Check if the user has permission to access this route
	# Set up connection to SQL Server database
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()
    #print(user)    successful
    if not user.CanDisplayQuiz:
        message = 'You are not allowed to run DISPLAY QUIZZES. Please see the Administrator.'
        return render_template('quiz_message.html', message=message)
    else:
 
        import subprocess

        subprocess.call(['python', 'display_quiz.py', str(user_id)])
        return 'display_quiz() execution successful.'
		
		
# FORMATIVE MENU
@app.route('/formative_menu/')
def formative_menu():
    global user_id
    return render_template('formative_menu.html')
	
@app.route('/add_formative', methods=['GET', 'POST'])
def add_formative():
    global user_id
    global xnow
	
	# Set up connection to SQL Server database
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
	
    cursor = conn.cursor()
	
	# Define the SELECT statement
    select_query2 = 'SELECT StudentNumber,FirstName,FamilyName FROM STUDENT'
    select_query3 = 'SELECT SectionCode,SectionName FROM SECTION'
    select_query4 = 'SELECT SubjectCode,SubjectName FROM SUBJECT'
    select_query5 = 'SELECT CampusCode,CampusName FROM CAMPUS'
	
	# Execute the query and fetch the results
    cursor.execute("SELECT TeacherID,TeacherName FROM TEACHER WHERE TeacherID=?",user_id)
    teachers = [(row[0], row[1]) for row in cursor.fetchall()]
	
    cursor.execute(select_query2)
    students = [(row[0], row[1].strip(), row[2].strip()) for row in cursor.fetchall()]
 
    cursor.execute(select_query3)
    sections = [(row[0], row[1]) for row in cursor.fetchall()]
	
    cursor.execute(select_query4)
    subjects = [(row[0], row[1]) for row in cursor.fetchall()]
	
    cursor.execute(select_query5)
    campuses = [(row[0], row[1]) for row in cursor.fetchall()]
	
    # Check if the user has permission to access this route
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()
    #print(user)
    if not user.CanAddFormative:
        message = 'You are not allowed to run ADD QUIZ. Please see the Administrator.'
        return render_template('formative_message.html', message=message)
		
    if request.method == 'POST':
        # Get the formative info from the form
        formativeno = request.form['formativeno']
        formativedate = request.form['formativedate']
        teachername = request.form['teachername']
        studentnumber = request.form['studentnumber']
        studentname = request.form['studentname']
        subjectname = request.form['subjectname']
        campusname = request.form['campusname']
        sectionname = request.form['sectionname']
        gradelevel = request.form['gradelevel']
        quarter = request.form['quarter']
        score = request.form['score']
        noofitems = request.form['noofitems']
        teacher_commentsfeedback = request.form['teacher_commentsfeedback']
		
        '''
        cursor.execute("SELECT * FROM FORMATIVE")
        rows = cursor.fetchall()
        for row in rows:
           print(row)
		'''
        # Set up connection to SQL Server database
        server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
        database = 'TransDB'
        username = 'sa'
        password = 'noabrir'
        driver = '{SQL Server}'

        conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
		
        # Check if a quiz with the same QuizNo already exists
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM FORMATIVE WHERE FormativeNo = ?", formativeno)
        row = cursor.fetchone()
        if row:
            # A formative with the same formativeno already exists
            message = 'A formative with Formative No. ' + formativeno + ' already exists.'
            return render_template('formative_message.html', message=message)
        else:
            # No formativeno with the same FormativeNo exists, so insert the new formative
            cursor.execute("INSERT INTO FORMATIVE (FormativeNo,FormativeDate,TeacherID,TeacherName,StudentNumber,StudentName,SubjectName,CampusName,SectionName,GradeLevel,Quarter,Score,NoOfItems,TeacherCommentsFeedback,CreatedBy,CreatedOn,UpdatedBy,UpdatedOn) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
              formativeno,formativedate,user_id,teachername,studentnumber,studentname,subjectname,campusname,sectionname,gradelevel,quarter,score,noofitems,teacher_commentsfeedback,user_id,xnow,user_id,xnow)
            conn.commit()

            message = 'New Formative No. ' + formativeno + ' added successfully.'
            return render_template('formative_message.html', message=message)
		
            #return message
 
    # If the request method is GET, show the add formative form
    return render_template('formative_add.html',teachers=teachers,students=students,sections=sections,subjects=subjects,campuses=campuses)

@app.route('/delete_formative', methods=['GET', 'POST'])	
def delete_formative():
    global user_id
    global xnow
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
	# Check if the user has permission to access this route
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()

    if not user.CanDeleteFormative:
        message = 'You are not allowed to run DELETE FORMATIVE. Please see the Administrator.'
        return render_template('formative_message.html', message=message)
		
    if request.method == 'POST':
        # Get the student info from the form
        formativeno = request.form['formativeno']
		
		# Check if quiz exists
        server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
        database = 'TransDB'
        username = 'sa'
        password = 'noabrir'
        driver = '{SQL Server}'

        conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
        cursor = conn.cursor()
		
        cursor.execute(f"SELECT * FROM FORMATIVE WHERE FormativeNo='{formativeno}'")
        existing_formative = cursor.fetchone()
        if existing_formative:
            sql = f"DELETE FROM FORMATIVE WHERE FormativeNo='{formativeno}'"
            cursor.execute(sql)
            conn.commit()
            #return 'Formative' + formativeno + ' successfully deleted.'
            message = 'Formative ' + formativeno + ' successfully deleted.'
            return render_template('formative_message.html', message=message)
        else:
            message = 'Formative No. ' + formativeno + ' does not exist.'
            return render_template('formative_message.html', message=message)
    return render_template('formative_delete.html')
	
@app.route('/update_formative1', methods=['GET', 'POST'])
def update_formative1():
    global user_id
    global xnow
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    cursor = conn.cursor()
	# Check if the user has permission to access this route
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()
    #print(user)	# successful, user has row values
    if not user.CanUpdateFormative:
        message = 'You are not allowed to run UPDATE FORMATIVE. Please see the Administrator.'
        return render_template('formative_message.html', message=message)
    return render_template('update_formative1.html')
	
@app.route('/update_formative2', methods=['GET', 'POST'])	
def update_formative2():
    if request.method == 'POST':
        # Get the formative info from the  update_formative1 form
        formativeno = request.form['formativeno']
    
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')	
    cursor = conn.cursor()
	
    # Define the SELECT statement
    select_query2 = 'SELECT StudentNumber,FirstName,FamilyName FROM STUDENT'
    select_query3 = 'SELECT SectionName FROM SECTION'
    select_query4 = 'SELECT SubjectName FROM SUBJECT'
    select_query5 = 'SELECT CampusName FROM CAMPUS'
	
	# Execute the query and fetch the results
    cursor.execute("SELECT * FROM TEACHER WHERE TeacherID=?", user_id)
    teachers = [(row[0], row[1]) for row in cursor.fetchall()]
	
    cursor.execute(select_query2)
    students = [(row[0], row[1], row[2]) for row in cursor.fetchall()]
 
    cursor.execute(select_query3)
    sections = [(row[0]) for row in cursor.fetchall()]
	
    cursor.execute(select_query4)
    subjects = [(row[0]) for row in cursor.fetchall()]
	
    cursor.execute(select_query5)
    campuses = [(row[0]) for row in cursor.fetchall()]
	
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'TransDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    cursor = conn.cursor()
	
    cursor.execute("SELECT * FROM FORMATIVE WHERE FormativeNo = ?", formativeno)
    formative = cursor.fetchone()
    #print(quiz)
    #print(teachers)
    return render_template('update_formative2.html',formative=formative,teachers=teachers,students=students,sections=sections,subjects=subjects,campuses=campuses)

@app.route('/update_formative', methods=['GET', 'POST'])
def update_formative():
    global user_id
    global xnow
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')	
    cursor = conn.cursor()

    # Check if the user has permission to access this route
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()
    #print(user)    # successful, user has values
    if not user.CanUpdateFormative:
        message = 'You are not allowed to run UPDATE FORMATIVE. Please see the Administrator.'
        return render_template('formative_message.html', message=message)
		
    if request.method == 'POST':
        # Get the formative info from the form
        formativeno = request.form['formativeno']
        formativedate = request.form['formativedate']
        teacherid = request.form['teacherid']
        teachername = request.form['teachername']
        studentnumber = request.form['studentnumber']
        studentname = request.form['studentname']
        subjectname = request.form['subjectname']
        campusname = request.form['campusname']
        sectionname = request.form['sectionname']
        gradelevel = request.form['gradelevel']
        quarter = request.form['quarter']
        score = request.form['score']
        noofitems = request.form['noofitems']
        teacher_commentsfeedback = request.form['teacher_commentsfeedback']
 
        # Check if a formative with the same Formative already exists
        server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
        database = 'TransDB'
        username = 'sa'
        password = 'noabrir'
        driver = '{SQL Server}'

        conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')	
		
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM FORMATIVE WHERE FormativeNo = ?", formativeno)
        existing_formative = cursor.fetchone()
        formative = existing_formative
		
        if existing_formative:
            update_query = "UPDATE FORMATIVE SET FormativeDate=?,TeacherID=?,TeacherName=?,StudentNumber=?,StudentName=?,SubjectName=?,CampusName=?,SectionName=?,GradeLevel=?,Score=?,NoOfItems=?,TeacherCommentsFeedback=?,CreatedBy=?,CreatedOn=?,UpdatedBy=?,UpdatedOn=? WHERE FormativeNo=?"
            cursor.execute(update_query, (formativedate,teacherid,teachername,studentnumber,studentname,subjectname,campusname,sectionname,gradelevel,score,noofitems,teacher_commentsfeedback,user_id,xnow,user_id,xnow,formativeno,))
            conn.commit()
            message = 'Formative No. ' + formativeno + ' successfully updated..'
            return render_template('formative_message.html', message=message)
        else:
            message = 'Formative No. ' + formativeno + ' does not exist.'
            return render_template('formative_message.html', message=message)
        
    # If the request method is GET
    return render_template('update_formative1.html')

	
@app.route('/query_formative', methods=['GET', 'POST'])	
def query_formative():
    global user_id
    global xnow
    #print (user_id)	# user_id=DM

    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    
    cursor = conn.cursor()
    cursor.execute("SELECT UserCode,UserType,CanQueryFormative FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()
    xuser=user[0]
    print('user_id = ' + user_id) # 20-120145-P
    print('xuser = ' + xuser)   # 20-120145-P
    part1, part2, part3 = xuser.split("-")
    print('part1 = ' + part1)  # 20
    print('part2 = ' + part2)  # 120145
    print('part3 = ' + part3)  # P
    xuser = part1 + '-' + part2
    print('xuser = ' + xuser)
    user_type=user[1] 
    print('user_type = ' + user_type)  # Parent
    
    if not user.CanQueryFormative:
        message = 'You are not allowed to run QUERY FORMATIVE. Please see the Administrator.'
        return render_template('formative_message.html', message=message)
		
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'TransDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    cursor = conn.cursor()
	
    if request.method == 'POST':
        formativeno = request.form['formativeno']
        cursor.execute(f"SELECT * FROM FORMATIVE WHERE FormativeNo='{formativeno}' and StudentNumber='{xuser}'")
        existing_formative = cursor.fetchone()

        if existing_formative:
            formative=existing_formative
            xformative=formative.FormativeDate
            year = xformative.strftime("%Y")
            month = xformative.strftime("%m")
            day = xformative.strftime("%d")
            xformativedate=year + '-' + month + '-' + day
            formative.FormativeDate = xformativedate 
            formative.StudentName=formative.StudentName.upper()

            return render_template('formative.html', formative=existing_formative)
        else:
           message = 'Formative No. ' + formativeno + ' does not exist or (the student is not yourself or is not your son/daughter/ward.)'
           return render_template('formative_message.html', message=message)
    return render_template('formative_query.html')
	

#@app.route('/index_formatives')
@app.route('/index_formatives', methods=['GET', 'POST'])	
def index_formatives():
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    database_transdb = 'TransDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn_masterdb = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    cursor_masterdb = conn_masterdb.cursor()
    cursor_masterdb.execute("SELECT UserCode, UserType FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor_masterdb.fetchone()
    #print('1-user.UserType = ' + user.UserType)   # 1-user.UserType = Student
    user.UserType = user.UserType.strip()
    '''
    if user.UserType=='Student' or user.UserType=='Parent' or user.UserType=='Guardian' or user.UserType=='Admin':
        cursor_masterdb.execute("SELECT TeacherName FROM TEACHER")
        teachers = cursor_masterdb.fetchall()
        print('2-user.UserType = ' + user.UserType)    # 2-user.UserType = Student
        for teacher in teachers:
            print('2-TeacherName = ' + teacher[0])
    elif user.UserType=='Teacher':
        teachers = []
        cursor_masterdb.execute("SELECT TeacherName FROM TEACHER WHERE TeacherID=?", user_id)
        teacher = cursor_masterdb.fetchone()
        if teacher is not None:
            teacher_name = teacher
            print('3-TeacherName = ' + str(teacher_name))    # 3-TeacherName = ('DINNIE MORALES                                              ',)
            teachers.append(teacher_name)
        else:
            print('No teacher found with the given TeacherID')
    '''
    # Fetch the students from the STUDENT table
    select_students_query = 'SELECT StudentNumber, FirstName, FamilyName FROM STUDENT'
 
    cursor_masterdb.execute(select_students_query)
    students = [(row[0], row[1].strip(), row[2].strip()) for row in cursor_masterdb.fetchall()]

    # Fetch the teachers from the TEACHER table
    cursor_masterdb.execute("SELECT TeacherName FROM TEACHER")   # WHERE TeacherID=?", user_id)
    teachers = cursor_masterdb.fetchall()

    # Fetch the sections from the SECTION table
    select_sections_query = 'SELECT SectionName FROM SECTION'
    cursor_masterdb.execute(select_sections_query)
    sections = cursor_masterdb.fetchall()

    # Fetch the subjects from the SUBJECT table
    select_subjects_query = 'SELECT SubjectName FROM SUBJECT'
    cursor_masterdb.execute(select_subjects_query)
    subjects = cursor_masterdb.fetchall()

    # Close the database connection
    #conn_masterdb.close()

    return render_template('index_formatives.html', students=students, teachers=teachers, sections=sections, subjects=subjects)

	
@app.route('/query_formatives', methods=['GET', 'POST'])	
def query_formatives():
    global user_id
    global xnow

    # Get the selected values from the form
    student_name = request.form['student_name']
    teacher_name = request.form['teacher_name']
    section_name = request.form['section_name']
    subject_name = request.form['subject_name']
    quarter_number = request.form['quarter_number']
    #print(student_name)   # Vincent II           Conti
    # Connect to the TransDB database
    database = 'TransDB'
    conn_transdb = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    cursor_transdb = conn_transdb.cursor()

    # Define the SELECT statement to fetch the formative scores
    select_formatives_query = '''
    SELECT FormativeNo, Score, NoOfItems FROM FORMATIVE WHERE StudentName=? AND TeacherName=? AND SectionName=? AND SubjectName=? AND Quarter=?
    '''
	# Execute the query and fetch the results
    cursor_transdb.execute(select_formatives_query, (student_name, teacher_name, section_name, subject_name, quarter_number))
    formatives = cursor_transdb.fetchall()

    # Close the TransDB database connection
    conn_transdb.close()

    return render_template('query_formatives.html', formatives=formatives, student_name=student_name, teacher_name=teacher_name, section_name=section_name, subject_name=subject_name, quarter_number=quarter_number)
	
@app.route('/display_formative/')
def display_formative():
    global user_id

    # Check if the user has permission to access this route
	# Set up connection to SQL Server database
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()
    #print(user)    successful
    if not user.CanDisplayFormative:
        message = 'You are not allowed to run DISPLAY FORMATIVES. Please see the Administrator.'
        return render_template('formative_message.html', message=message)
    else:
 
        import subprocess

        subprocess.call(['python', 'display_formative.py', str(user_id)])
        return 'display_formative() execution successful.'
		
		
# ALTERNATIVE MENU
@app.route('/alternative_menu/')
def alternative_menu():
    global user_id
    return render_template('alternative_menu.html')
	
@app.route('/add_alternative', methods=['GET', 'POST'])
def add_alternative():
    global user_id
    global xnow
	
	# Set up connection to SQL Server database
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
	
    cursor = conn.cursor()
	
	# Define the SELECT statement
    select_query2 = 'SELECT StudentNumber,FirstName,FamilyName FROM STUDENT'
    select_query3 = 'SELECT SectionCode,SectionName FROM SECTION'
    select_query4 = 'SELECT SubjectCode,SubjectName FROM SUBJECT'
    select_query5 = 'SELECT CampusCode,CampusName FROM CAMPUS'
	
	# Execute the query and fetch the results
    cursor.execute("SELECT TeacherID,TeacherName FROM TEACHER WHERE TeacherID=?",user_id)
    teachers = [(row[0], row[1]) for row in cursor.fetchall()]
	
    cursor.execute(select_query2)
    students = [(row[0], row[1].strip(), row[2].strip()) for row in cursor.fetchall()]
 
    cursor.execute(select_query3)
    sections = [(row[0], row[1]) for row in cursor.fetchall()]
	
    cursor.execute(select_query4)
    subjects = [(row[0], row[1]) for row in cursor.fetchall()]
	
    cursor.execute(select_query5)
    campuses = [(row[0], row[1]) for row in cursor.fetchall()]
	
    # Check if the user has permission to access this route
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()
    #print(user)
    if not user.CanAddAlternative:
        message = 'You are not allowed to run ADD ALTERNATIVE. Please see the Administrator.'
        return render_template('alternative_message.html', message=message)
		
    if request.method == 'POST':
        # Get the alternative info from the form
        alternativeno = request.form['alternativeno']
        alternativedate = request.form['alternativedate']
        teachername = request.form['teachername']
        studentnumber = request.form['studentnumber']
        studentname = request.form['studentname']
        subjectname = request.form['subjectname']
        campusname = request.form['campusname']
        sectionname = request.form['sectionname']
        gradelevel = request.form['gradelevel']
        quarter = request.form['quarter']
        alternative_type = request.form['alternative_type']
        score = request.form['score']
        noofitems = request.form['noofitems']
        teacher_commentsfeedback = request.form['teacher_commentsfeedback']
        '''
        cursor.execute("SELECT * FROM ALTERNATIVE")
        rows = cursor.fetchall()
        for row in rows:
           print(row)
		'''
        # Set up connection to SQL Server database
        server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
        database = 'TransDB'
        username = 'sa'
        password = 'noabrir'
        driver = '{SQL Server}'

        conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
		
        # Check if a alternative with the same AlternativeNo already exists
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ALTERNATIVE WHERE alternativeNo = ?", alternativeno)
        row = cursor.fetchone()
        if row:
            # A alternative with the same alternativeno already exists
            message = 'A alternative with Alternative No. ' + alternativeno + ' already exists.'
            return render_template('alternative_message.html', message=message)
        else:
            # No formativeno with the same FormativeNo exists, so insert the new formative
            cursor.execute("INSERT INTO ALTERNATIVE (AlternativeNo,AlternativeDate,TeacherID,TeacherName,StudentNumber,StudentName,SubjectName,CampusName,SectionName,GradeLevel,Quarter,AlternativeType,Score,NoOfItems,TeacherCommentsFeedback,CreatedBy,CreatedOn,UpdatedBy,UpdatedOn) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
              alternativeno,alternativedate,user_id,teachername,studentnumber,studentname,subjectname,campusname,sectionname,gradelevel,quarter,alternative_type,score,noofitems,teacher_commentsfeedback,user_id,xnow,user_id,xnow)
            conn.commit()

            message = 'New Alternative No. ' + alternativeno + ' added successfully.'
            return render_template('alternative_message.html', message=message)

    # If the request method is GET, show the add alternative form
    return render_template('alternative_add.html',teachers=teachers,students=students,sections=sections,subjects=subjects,campuses=campuses)

@app.route('/delete_alternative', methods=['GET', 'POST'])	
def delete_alternative():
    global user_id
    global xnow
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
	# Check if the user has permission to access this route
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()

    if not user.CanDeleteAlternative:
        message = 'You are not allowed to run DELETE ALTERNATIVE. Please see the Administrator.'
        return render_template('alternative_message.html', message=message)
		
    if request.method == 'POST':
        # Get the student info from the form
        alternativeno = request.form['alternativeno']
		
		# Check if quiz exists
        server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
        database = 'TransDB'
        username = 'sa'
        password = 'noabrir'
        driver = '{SQL Server}'

        conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
        cursor = conn.cursor()
		
        cursor.execute(f"SELECT * FROM ALTERNATIVE WHERE AlternativeNo='{alternativeno}'")
        existing_alternative = cursor.fetchone()
        if existing_alternative:
            sql = f"DELETE FROM ALTERNATIVE WHERE AlternativeNo='{alternativeno}'"
            cursor.execute(sql)
            conn.commit()
            #return 'Alternative' + alternativeno + ' successfully deleted.'
            message = 'Alternative ' + alternativeno + ' successfully deleted.'
            return render_template('alternative_message.html', message=message)
        else:
            message = 'Alternative No. ' + alternativeno + ' does not exist.'
            return render_template('alternative_message.html', message=message)
    return render_template('alternative_delete.html')
	
@app.route('/update_alternative1', methods=['GET', 'POST'])
def update_alternative1():
    global user_id
    global xnow
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    cursor = conn.cursor()
	# Check if the user has permission to access this route
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()
    #print(user)	# successful, user has row values
    if not user.CanUpdateAlternative:
        message = 'You are not allowed to run UPDATE ALTERNATIVE. Please see the Administrator.'
        return render_template('alternative_message.html', message=message)
    return render_template('update_alternative1.html')
	
@app.route('/update_alternative2', methods=['GET', 'POST'])	
def update_alternative2():
    if request.method == 'POST':
        # Get the alternative info from the  update_alternative1 form
        alternativeno = request.form['alternativeno']
    
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')	
    cursor = conn.cursor()
	
    # Define the SELECT statement
    select_query2 = 'SELECT StudentNumber,FirstName,FamilyName FROM STUDENT'
    select_query3 = 'SELECT SectionName FROM SECTION'
    select_query4 = 'SELECT SubjectName FROM SUBJECT'
    select_query5 = 'SELECT CampusName FROM CAMPUS'
	
	# Execute the query and fetch the results
    cursor.execute("SELECT * FROM TEACHER WHERE TeacherID=?", user_id)
    teachers = [(row[0], row[1]) for row in cursor.fetchall()]
	
    cursor.execute(select_query2)
    students = [(row[0], row[1], row[2]) for row in cursor.fetchall()]
 
    cursor.execute(select_query3)
    sections = [(row[0]) for row in cursor.fetchall()]
	
    cursor.execute(select_query4)
    subjects = [(row[0]) for row in cursor.fetchall()]
	
    cursor.execute(select_query5)
    campuses = [(row[0]) for row in cursor.fetchall()]
	
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'TransDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    cursor = conn.cursor()
	
    cursor.execute("SELECT * FROM ALTERNATIVE WHERE AlternativeNo = ?", alternativeno)
    alternative = cursor.fetchone()
 
    return render_template('update_alternative2.html',alternative=alternative,teachers=teachers,students=students,sections=sections,subjects=subjects,campuses=campuses)

@app.route('/update_alternative', methods=['GET', 'POST'])
def update_alternative():
    global user_id
    global xnow
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')	
    cursor = conn.cursor()

    # Check if the user has permission to access this route
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()
    #print(user)    # successful, user has values
    if not user.CanUpdateAlternative:
        message = 'You are not allowed to run UPDATE ALTERNATIVE. Please see the Administrator.'
        return render_template('alternative_message.html', message=message)
		
    if request.method == 'POST':
        # Get the alternative info from the form
        alternativeno = request.form['alternativeno']
        alternativedate = request.form['alternativedate']
        teacherid = request.form['teacherid']
        teachername = request.form['teachername']
        studentnumber = request.form['studentnumber']
        studentname = request.form['studentname']
        subjectname = request.form['subjectname']
        campusname = request.form['campusname']
        sectionname = request.form['sectionname']
        gradelevel = request.form['gradelevel']
        quarter = request.form['quarter']
        alternative_type = request.form['alternative_type']
        score = request.form['score']
        noofitems = request.form['noofitems']
        teacher_commentsfeedback = request.form['teacher_commentsfeedback']
 
        # Check if a alternative with the same Alternative already exists
        server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
        database = 'TransDB'
        username = 'sa'
        password = 'noabrir'
        driver = '{SQL Server}'

        conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')	
		
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ALTERNATIVE WHERE AlternativeNo = ?", alternativeno)
        existing_alternative = cursor.fetchone()
        alternative = existing_alternative
		
        if existing_alternative:
            update_query = "UPDATE ALTERNATIVE SET AlternativeDate=?,TeacherID=?,TeacherName=?,StudentNumber=?,StudentName=?,SubjectName=?,CampusName=?,SectionName=?,GradeLevel=?,AlternativeType=?,Score=?,NoOfItems=?,TeacherCommentsFeedback=?,CreatedBy=?,CreatedOn=?,UpdatedBy=?,UpdatedOn=? WHERE AlternativeNo=?"
            cursor.execute(update_query, (alternativedate,teacherid,teachername,studentnumber,studentname,subjectname,campusname,sectionname,gradelevel,alternative_type,score,noofitems,teacher_commentsfeedback,user_id,xnow,user_id,xnow,alternativeno,))
            conn.commit()
            message = 'Alternative No. ' + alternativeno + ' successfully updated..'
            return render_template('alternative_message.html', message=message)
        else:
            message = 'Alternative No. ' + alternativeno + ' does not exist.'
            return render_template('alternative_message.html', message=message)
        
    # If the request method is GET
    return render_template('update_alternative1.html')

	
@app.route('/query_alternative', methods=['GET', 'POST'])	
def query_alternative():
    global user_id
    global xnow
    #print (user_id)	# user_id=DM

    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    
    cursor = conn.cursor()
    cursor.execute("SELECT UserCode,UserType,CanQueryAlternative FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()
    xuser=user[0]
    print('user_id = ' + user_id) # 20-120145-P
    print('xuser = ' + xuser)   # 20-120145-P
    part1, part2, part3 = xuser.split("-")
    print('part1 = ' + part1)  # 20
    print('part2 = ' + part2)  # 120145
    print('part3 = ' + part3)  # P
    xuser = part1 + '-' + part2
    print('xuser = ' + xuser)
    user_type=user[1] 
    print('user_type = ' + user_type)  # Parent or Guardian
    
    if not user.CanQueryAlternative:
        message = 'You are not allowed to run QUERY ALTERNATIVE. Please see the Administrator.'
        return render_template('alternative_message.html', message=message)
		
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'TransDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    cursor = conn.cursor()
	
    if request.method == 'POST':
        alternativeno = request.form['alternativeno']
        cursor.execute(f"SELECT * FROM ALTERNATIVE WHERE AlternativeNo='{alternativeno}' and StudentNumber='{xuser}'")
        existing_alternative = cursor.fetchone()

        if existing_alternative:
            alternative=existing_alternative
            xalternative=alternative.AlternativeDate
            year = xalternative.strftime("%Y")
            month = xalternative.strftime("%m")
            day = xalternative.strftime("%d")
            xalternativedate=year + '-' + month + '-' + day
            alternative.AlternativeDate = xalternativedate 
            alternative.StudentName=alternative.StudentName.upper()

            return render_template('alternative.html', alternative=existing_alternative)
        else:
           message = 'Alternative No. ' + alternativeno + ' does not exist or (the student is not yourself or is not your son/daughter/ward.)'
           return render_template('alternative_message.html', message=message)
    return render_template('alternative_query.html')
	

#@app.route('/index_alternatives')
@app.route('/index_alternatives', methods=['GET', 'POST'])	
def index_alternatives():
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    database_transdb = 'TransDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn_masterdb = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    cursor_masterdb = conn_masterdb.cursor()
    cursor_masterdb.execute("SELECT UserCode, UserType FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor_masterdb.fetchone()
    #print('1-user.UserType = ' + user.UserType)   # 1-user.UserType = Student
    user.UserType = user.UserType.strip()
    '''
    if user.UserType=='Student' or user.UserType=='Parent' or user.UserType=='Guardian' or user.UserType=='Admin':
        cursor_masterdb.execute("SELECT TeacherName FROM TEACHER")
        teachers = cursor_masterdb.fetchall()
        print('2-user.UserType = ' + user.UserType)    # 2-user.UserType = Student
        for teacher in teachers:
            print('2-TeacherName = ' + teacher[0])
    elif user.UserType=='Teacher':
        teachers = []
        cursor_masterdb.execute("SELECT TeacherName FROM TEACHER WHERE TeacherID=?", user_id)
        teacher = cursor_masterdb.fetchone()
        if teacher is not None:
            teacher_name = teacher
            print('3-TeacherName = ' + str(teacher_name))    # 3-TeacherName = ('DINNIE MORALES                                              ',)
            teachers.append(teacher_name)
        else:
            print('No teacher found with the given TeacherID')
    '''
    # Fetch the students from the STUDENT table
    select_students_query = 'SELECT StudentNumber, FirstName, FamilyName FROM STUDENT'
 
    cursor_masterdb.execute(select_students_query)
    students = [(row[0], row[1].strip(), row[2].strip()) for row in cursor_masterdb.fetchall()]

    # Fetch the teachers from the TEACHER table
    cursor_masterdb.execute("SELECT TeacherName FROM TEACHER")   # WHERE TeacherID=?", user_id)
    teachers = cursor_masterdb.fetchall()

    # Fetch the sections from the SECTION table
    select_sections_query = 'SELECT SectionName FROM SECTION'
    cursor_masterdb.execute(select_sections_query)
    sections = cursor_masterdb.fetchall()

    # Fetch the subjects from the SUBJECT table
    select_subjects_query = 'SELECT SubjectName FROM SUBJECT'
    cursor_masterdb.execute(select_subjects_query)
    subjects = cursor_masterdb.fetchall()

    # Close the database connection
    #conn_masterdb.close()

    return render_template('index_alternatives.html', students=students, teachers=teachers, sections=sections, subjects=subjects)

	
@app.route('/query_alternatives', methods=['GET', 'POST'])	
def query_alternatives():
    global user_id
    global xnow

    # Get the selected values from the form
    student_name = request.form['student_name']
    teacher_name = request.form['teacher_name']
    section_name = request.form['section_name']
    subject_name = request.form['subject_name']
    quarter_number = request.form['quarter_number']
    #print(teacher_name)   
    # Connect to the TransDB database
    database = 'TransDB'
    conn_transdb = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    cursor_transdb = conn_transdb.cursor()

    # Define the SELECT statement to fetch the alternative scores
    select_alternatives_query = '''
    SELECT AlternativeNo, Score, NoOfItems FROM ALTERNATIVE WHERE StudentName=? AND TeacherName=? AND SectionName=? AND SubjectName=? AND Quarter=?
    '''
	# Execute the query and fetch the results
    cursor_transdb.execute(select_alternatives_query, (student_name, teacher_name, section_name, subject_name, quarter_number))
    alternatives = cursor_transdb.fetchall()

    # Close the TransDB database connection
    conn_transdb.close()

    return render_template('query_alternatives.html', alternatives=alternatives, student_name=student_name, teacher_name=teacher_name, section_name=section_name, subject_name=subject_name, quarter_number=quarter_number)
	
@app.route('/display_alternative/')
def display_alternative():
    global user_id

    # Check if the user has permission to access this route
	# Set up connection to SQL Server database
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()
    #print(user)    successful
    if not user.CanDisplayAlternative:
        message = 'You are not allowed to run DISPLAY ALTERNATIVES. Please see the Administrator.'
        return render_template('alternative_message.html', message=message)
    else:
 
        import subprocess

        subprocess.call(['python', 'display_alternative.py', str(user_id)])
        return 'display_alternative() execution successful.'
		
		
# PERIO MENU
@app.route('/perio_menu/')
def perio_menu():
    global user_id
    return render_template('perio_menu.html')
	
@app.route('/add_perio', methods=['GET', 'POST'])
def add_perio():
    global user_id
    global xnow
	
	# Set up connection to SQL Server database
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
	
    cursor = conn.cursor()
	
	# Define the SELECT statement
    select_query2 = 'SELECT StudentNumber,FirstName,FamilyName FROM STUDENT'
    select_query3 = 'SELECT SectionCode,SectionName FROM SECTION'
    select_query4 = 'SELECT SubjectCode,SubjectName FROM SUBJECT'
    select_query5 = 'SELECT CampusCode,CampusName FROM CAMPUS'
	
	# Execute the query and fetch the results
    cursor.execute("SELECT TeacherID,TeacherName FROM TEACHER WHERE TeacherID=?",user_id)
    teachers = [(row[0], row[1]) for row in cursor.fetchall()]
	
    cursor.execute(select_query2)
    students = [(row[0], row[1].strip(), row[2].strip()) for row in cursor.fetchall()]
 
    cursor.execute(select_query3)
    sections = [(row[0], row[1]) for row in cursor.fetchall()]
	
    cursor.execute(select_query4)
    subjects = [(row[0], row[1]) for row in cursor.fetchall()]
	
    cursor.execute(select_query5)
    campuses = [(row[0], row[1]) for row in cursor.fetchall()]
	
    # Check if the user has permission to access this route
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()
    #print(user)
    if not user.CanAddPerio:
        message = 'You are not allowed to run ADD PERIO. Please see the Administrator.'
        return render_template('perio_message.html', message=message)
		
    if request.method == 'POST':
        # Get the perio info from the form
        periono = request.form['periono']
        periodate = request.form['periodate']
        teachername = request.form['teachername']
        studentnumber = request.form['studentnumber']
        studentname = request.form['studentname']
        subjectname = request.form['subjectname']
        campusname = request.form['campusname']
        sectionname = request.form['sectionname']
        gradelevel = request.form['gradelevel']
        quarter = request.form['quarter']
        score = request.form['score']
        noofitems = request.form['noofitems']
        teacher_commentsfeedback = request.form['teacher_commentsfeedback']
        '''
        cursor.execute("SELECT * FROM PERIO")
        rows = cursor.fetchall()
        for row in rows:
           print(row)
		'''
        # Set up connection to SQL Server database
        server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
        database = 'TransDB'
        username = 'sa'
        password = 'noabrir'
        driver = '{SQL Server}'

        conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
		
        # Check if a alternative with the same AlternativeNo already exists
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM PERIO WHERE PerioNo = ?", periono)
        row = cursor.fetchone()
        if row:
            # A perio with the same periono already exists
            message = 'A perio with Perio No. ' + periono + ' already exists.'
            return render_template('perio_message.html', message=message)
        else:
            # No formativeno with the same PerioNo exists, so insert the new perio
            cursor.execute("INSERT INTO PERIO (PerioNo,PerioDate,TeacherID,TeacherName,StudentNumber,StudentName,SubjectName,CampusName,SectionName,GradeLevel,Quarter,Score,NoOfItems,TeacherCommentsFeedback,CreatedBy,CreatedOn,UpdatedBy,UpdatedOn) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
              periono,periodate,user_id,teachername,studentnumber,studentname,subjectname,campusname,sectionname,gradelevel,quarter,score,noofitems,teacher_commentsfeedback,user_id,xnow,user_id,xnow)
            conn.commit()

            message = 'New Perio No. ' + periono + ' added successfully.'
            return render_template('perio_message.html', message=message)

    # If the request method is GET, show the add perio form
    return render_template('perio_add.html',teachers=teachers,students=students,sections=sections,subjects=subjects,campuses=campuses)

@app.route('/delete_perio', methods=['GET', 'POST'])	
def delete_perio():
    global user_id
    global xnow
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
	# Check if the user has permission to access this route
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()

    if not user.CanDeletePerio:
        message = 'You are not allowed to run DELETE PERIO. Please see the Administrator.'
        return render_template('perio_message.html', message=message)
		
    if request.method == 'POST':
        # Get the student info from the form
        periono = request.form['periono']
		
		# Check if perio exists
        server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
        database = 'TransDB'
        username = 'sa'
        password = 'noabrir'
        driver = '{SQL Server}'

        conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
        cursor = conn.cursor()
		
        cursor.execute(f"SELECT * FROM PERIO WHERE PerioNo='{periono}'")
        existing_perio = cursor.fetchone()
        if existing_perio:
            sql = f"DELETE FROM PERIO WHERE PerioNo='{periono}'"
            cursor.execute(sql)
            conn.commit()
            #return 'Perio' + periono + ' successfully deleted.'
            message = 'Perio ' + periono + ' successfully deleted.'
            return render_template('perio_message.html', message=message)
        else:
            message = 'Perio No. ' + periono + ' does not exist.'
            return render_template('perio_message.html', message=message)
    return render_template('perio_delete.html')
	
@app.route('/update_perio1', methods=['GET', 'POST'])
def update_perio1():
    global user_id
    global xnow
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    cursor = conn.cursor()
	# Check if the user has permission to access this route
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()
    #print(user)	# successful, user has row values
    if not user.CanUpdatePerio:
        message = 'You are not allowed to run UPDATE PERIO. Please see the Administrator.'
        return render_template('perio_message.html', message=message)
    return render_template('update_perio1.html')
	
@app.route('/update_perio2', methods=['GET', 'POST'])	
def update_perio2():
    if request.method == 'POST':
        # Get the perio info from the  update_perio1 form
        periono = request.form['periono']
    
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')	
    cursor = conn.cursor()
	
    # Define the SELECT statement
    select_query2 = 'SELECT StudentNumber,FirstName,FamilyName FROM STUDENT'
    select_query3 = 'SELECT SectionName FROM SECTION'
    select_query4 = 'SELECT SubjectName FROM SUBJECT'
    select_query5 = 'SELECT CampusName FROM CAMPUS'
	
	# Execute the query and fetch the results
    cursor.execute("SELECT * FROM TEACHER WHERE TeacherID=?", user_id)
    teachers = [(row[0], row[1]) for row in cursor.fetchall()]
	
    cursor.execute(select_query2)
    students = [(row[0], row[1], row[2]) for row in cursor.fetchall()]
 
    cursor.execute(select_query3)
    sections = [(row[0]) for row in cursor.fetchall()]
	
    cursor.execute(select_query4)
    subjects = [(row[0]) for row in cursor.fetchall()]
	
    cursor.execute(select_query5)
    campuses = [(row[0]) for row in cursor.fetchall()]
	
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'TransDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    cursor = conn.cursor()
	
    cursor.execute("SELECT * FROM PERIO WHERE PerioNo = ?", periono)
    perio = cursor.fetchone()
 
    return render_template('update_perio2.html',perio=perio,teachers=teachers,students=students,sections=sections,subjects=subjects,campuses=campuses)

@app.route('/update_perio', methods=['GET', 'POST'])
def update_perio():
    global user_id
    global xnow
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')	
    cursor = conn.cursor()

    # Check if the user has permission to access this route
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()
    #print(user)    # successful, user has values
    if not user.CanUpdatePerio:
        message = 'You are not allowed to run UPDATE PERIO. Please see the Administrator.'
        return render_template('perio_message.html', message=message)
		
    if request.method == 'POST':
        # Get the perio info from the form
        periono = request.form['periono']
        periodate = request.form['periodate']
        teacherid = request.form['teacherid']
        teachername = request.form['teachername']
        studentnumber = request.form['studentnumber']
        studentname = request.form['studentname']
        subjectname = request.form['subjectname']
        campusname = request.form['campusname']
        sectionname = request.form['sectionname']
        gradelevel = request.form['gradelevel']
        quarter = request.form['quarter']
        score = request.form['score']
        noofitems = request.form['noofitems']
        teacher_commentsfeedback = request.form['teacher_commentsfeedback']
 
        # Check if a perio with the same Perio No. already exists
        server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
        database = 'TransDB'
        username = 'sa'
        password = 'noabrir'
        driver = '{SQL Server}'

        conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')	
		
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM PERIO WHERE PerioNo = ?", periono)
        existing_perio = cursor.fetchone()
        perio = existing_perio
		
        if existing_perio:
            update_query = "UPDATE PERIO SET PerioDate=?,TeacherID=?,TeacherName=?,StudentNumber=?,StudentName=?,SubjectName=?,CampusName=?,SectionName=?,GradeLevel=?,Score=?,NoOfItems=?,TeacherCommentsFeedback=?,CreatedBy=?,CreatedOn=?,UpdatedBy=?,UpdatedOn=? WHERE perioNo=?"
            cursor.execute(update_query, (periodate,teacherid,teachername,studentnumber,studentname,subjectname,campusname,sectionname,gradelevel,score,noofitems,teacher_commentsfeedback,user_id,xnow,user_id,xnow,periono,))
            conn.commit()
            message = 'Perio No. ' + periono + ' successfully updated..'
            return render_template('perio_message.html', message=message)
        else:
            message = 'Perio No. ' + periono + ' does not exist.'
            return render_template('perio_message.html', message=message)
        
    # If the request method is GET
    return render_template('update_perio1.html')

	
@app.route('/query_perio', methods=['GET', 'POST'])	
def query_perio():
    global user_id
    global xnow
    #print (user_id)	# user_id=DM

    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    
    cursor = conn.cursor()
    cursor.execute("SELECT UserCode,UserType,CanQueryPerio FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()
    xuser=user[0]
    print('user_id = ' + user_id) # 20-120145-P
    print('xuser = ' + xuser)   # 20-120145-P
    part1, part2, part3 = xuser.split("-")
    print('part1 = ' + part1)  # 20
    print('part2 = ' + part2)  # 120145
    print('part3 = ' + part3)  # P
    xuser = part1 + '-' + part2
    print('xuser = ' + xuser)
    user_type=user[1] 
    print('user_type = ' + user_type)  # Parent or Guardian
    
    if not user.CanQueryPerio:
        message = 'You are not allowed to run QUERY PERIO. Please see the Administrator.'
        return render_template('perio_message.html', message=message)
		
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'TransDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    cursor = conn.cursor()
	
    if request.method == 'POST':
        periono = request.form['periono']
        cursor.execute(f"SELECT * FROM PERIO WHERE PerioNo='{periono}' and StudentNumber='{xuser}'")
        existing_perio = cursor.fetchone()

        if existing_perio:
            perio=existing_perio
            xperio=perio.PerioDate
            year = xperio.strftime("%Y")
            month = xperio.strftime("%m")
            day = xperio.strftime("%d")
            xperiodate=year + '-' + month + '-' + day
            perio.PerioDate = xperiodate 
            perio.StudentName=perio.StudentName.upper()

            return render_template('perio.html', perio=existing_perio)
        else:
           message = 'Perio No. ' + periono + ' does not exist or (the student is not yourself or is not your son/daughter/ward.)'
           return render_template('perio_message.html', message=message)
    return render_template('perio_query.html')
	

#@app.route('/index_perios')
@app.route('/index_perios', methods=['GET', 'POST'])	
def index_perios():
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    database_transdb = 'TransDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn_masterdb = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    cursor_masterdb = conn_masterdb.cursor()
    cursor_masterdb.execute("SELECT UserCode, UserType FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor_masterdb.fetchone()
    #print('1-user.UserType = ' + user.UserType)   # 1-user.UserType = Student
    user.UserType = user.UserType.strip()
    '''
    if user.UserType=='Student' or user.UserType=='Parent' or user.UserType=='Guardian' or user.UserType=='Admin':
        cursor_masterdb.execute("SELECT TeacherName FROM TEACHER")
        teachers = cursor_masterdb.fetchall()
        print('2-user.UserType = ' + user.UserType)    # 2-user.UserType = Student
        for teacher in teachers:
            print('2-TeacherName = ' + teacher[0])
    elif user.UserType=='Teacher':
        teachers = []
        cursor_masterdb.execute("SELECT TeacherName FROM TEACHER WHERE TeacherID=?", user_id)
        teacher = cursor_masterdb.fetchone()
        if teacher is not None:
            teacher_name = teacher
            print('3-TeacherName = ' + str(teacher_name))    # 3-TeacherName = ('DINNIE MORALES                                              ',)
            teachers.append(teacher_name)
        else:
            print('No teacher found with the given TeacherID')
    '''
    # Fetch the students from the STUDENT table
    select_students_query = 'SELECT StudentNumber, FirstName, FamilyName FROM STUDENT'
 
    cursor_masterdb.execute(select_students_query)
    students = [(row[0], row[1].strip(), row[2].strip()) for row in cursor_masterdb.fetchall()]

    # Fetch the teachers from the TEACHER table
    cursor_masterdb.execute("SELECT TeacherName FROM TEACHER")   # WHERE TeacherID=?", user_id)
    teachers = cursor_masterdb.fetchall()

    # Fetch the sections from the SECTION table
    select_sections_query = 'SELECT SectionName FROM SECTION'
    cursor_masterdb.execute(select_sections_query)
    sections = cursor_masterdb.fetchall()

    # Fetch the subjects from the SUBJECT table
    select_subjects_query = 'SELECT SubjectName FROM SUBJECT'
    cursor_masterdb.execute(select_subjects_query)
    subjects = cursor_masterdb.fetchall()

    # Close the database connection
    #conn_masterdb.close()

    return render_template('index_perios.html', students=students, teachers=teachers, sections=sections, subjects=subjects)

	
@app.route('/query_perios', methods=['GET', 'POST'])	
def query_perios():
    global user_id
    global xnow

    # Get the selected values from the form
    student_name = request.form['student_name']
    teacher_name = request.form['teacher_name']
    section_name = request.form['section_name']
    subject_name = request.form['subject_name']
    quarter_number = request.form['quarter_number']
    #print(teacher_name)   
    # Connect to the TransDB database
    database = 'TransDB'
    conn_transdb = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    cursor_transdb = conn_transdb.cursor()

    # Define the SELECT statement to fetch the perio scores
    select_perios_query = '''
    SELECT PerioNo, Score, NoOfItems FROM PERIO WHERE StudentName=? AND TeacherName=? AND SectionName=? AND SubjectName=? AND Quarter=?
    '''
	# Execute the query and fetch the results
    cursor_transdb.execute(select_perios_query, (student_name, teacher_name, section_name, subject_name, quarter_number))
    perios = cursor_transdb.fetchall()
    print(student_name)
    # Close the TransDB database connection
    conn_transdb.close()

    return render_template('query_perios.html', perios=perios, student_name=student_name, teacher_name=teacher_name, section_name=section_name, subject_name=subject_name, quarter_number=quarter_number)
	
@app.route('/display_perio/')
def display_perio():
    global user_id

    # Check if the user has permission to access this route
	# Set up connection to SQL Server database
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database = 'MasterDB'
    username = 'sa'
    password = 'noabrir'
    driver = '{SQL Server}'

    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LOGIN WHERE UserCode=?", user_id)
    user = cursor.fetchone()
    #print(user)    successful
    if not user.CanDisplayPerio:
        message = 'You are not allowed to run DISPLAY PERIOS. Please see the Administrator.'
        return render_template('perio_message.html', message=message)
    else:
 
        import subprocess

        subprocess.call(['python', 'display_perio.py', str(user_id)])
        return 'display_perio() execution successful.'
		
		
# STUDENT QUARTERLY ASSESSMENT REPORT
@app.route('/')  
@app.route('/gradecomp_menu/')
def gradecomp_menu():
    global user_id
    return render_template('gradecomp_menu.html', user_id=user_id)

@app.route('/select_teacher', methods=['GET', 'POST'])
def select_teacher():
    global user_id
    global xnow
    cursor = conn.cursor()
	
    select_teachers_query = 'SELECT TeacherName FROM TEACHER'
    cursor_masterdb.execute(select_teachers_query)
    teachers = [row[0].strip() for row in cursor_masterdb.fetchall()]
    teachers = teachers

    return render_template('select_teacher.html',teachers=teachers)
	
@app.route('/select_teacher2', methods=['GET', 'POST'])
def select_teacher2():
    global user_id
    global xnow
    cursor = conn.cursor()
	
    select_teachers_query = 'SELECT TeacherName FROM TEACHER'
    cursor_masterdb.execute(select_teachers_query)
    teachers = [row[0].strip() for row in cursor_masterdb.fetchall()]
    teachers = teachers

    return render_template('select_teacher2.html',teachers=teachers)

@app.route('/tentative_assessment', methods=['GET', 'POST'])
def tentative_assessment():
    global user_id
    global xnow
	
    from flask import Flask, render_template, request
    import pyodbc
    from decimal import Decimal, ROUND_HALF_UP

    # Replace these values with your SQL Server credentials
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database_masterdb = 'MasterDB'
    database_transdb = 'TransDB'
    username = 'sa'
    password = 'noabrir'

    # Create a connection string
    conn_str_masterdb = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database_masterdb};UID={username};PWD={password}'
    conn_str_transdb = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database_transdb};UID={username};PWD={password}'
 
    # Connect to the MasterDB database
    conn_masterdb = pyodbc.connect(conn_str_masterdb)
    cursor_masterdb = conn_masterdb.cursor()

    # Fetch the campuses from the CAMPUS table
    select_campuses_query = 'SELECT CampusName FROM CAMPUS'
    cursor_masterdb.execute(select_campuses_query)
    campuses = cursor_masterdb.fetchall()

    # Fetch the teachers from the TEACHER table
    teacher_name = request.form['teacher_name']
    select_teachers_query = 'SELECT TeacherName FROM TEACHER WHERE TeacherName=?'
    cursor_masterdb.execute(select_teachers_query,teacher_name)
    teachers = cursor_masterdb.fetchone()

    # Fetch the subjects from the SUBJECT table
    select_subjects_query = 'SELECT SubjectName,QuizWeight,FormativeWeight,AlternativeWeight,PerioWeight,TeacherName FROM SUBJECT WHERE TeacherName=?'
    cursor_masterdb.execute(select_subjects_query,teacher_name)
    #subjects = cursor_masterdb.fetchall()
    subjects = [(row[0], row[1], row[2], row[3], row[4]) for row in cursor_masterdb.fetchall()]

    # Fetch the students from the STUDENT table
    select_students_query = 'SELECT StudentNumber, FirstName, FamilyName FROM STUDENT'
    cursor_masterdb.execute(select_students_query)
    #students = cursor_masterdb.fetchall()
    students = [(row[0], row[1].strip(), row[2].strip()) for row in cursor_masterdb.fetchall()]
    student = students
 
    # Close the database connection
    conn_masterdb.close()
    
    return render_template('compute_index.html', campuses=campuses, teachers=teachers, subjects=subjects, students=students,student=student)

@app.route('/display_student_performance_report', methods=['GET', 'POST'])	
def display_student_performance_report():
    from flask import request
    #print('request.method = ' + request.method)
    if request.method == 'POST':
        # Get the campus info from the  compute_index form
        campus_name = request.form['campus_name']
        teacher_name = request.form['teacher_name']
        subject_name = request.form['subject_name']
        quiz_weight = request.form['quiz_weight']
        formative_weight = request.form['formative_weight']
        alternative_weight = request.form['alternative_weight']
        perio_weight = request.form['perio_weight']
        glevel = request.form['glevel']
        student_number = request.form['student_number']
        student_name = request.form['student_name']
        quarter_number = request.form['quarter_number']
		
        student_name = student_name.upper()
		
    global user_id
    global xnow
	
    from flask import Flask, render_template, request
    import pyodbc
    from decimal import Decimal, ROUND_HALF_UP

    # Replace these values with your SQL Server credentials
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database_masterdb = 'MasterDB'
    database_transdb = 'TransDB'
    username = 'sa'
    password = 'noabrir'

    # Create a connection string
    conn_str_masterdb = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database_masterdb};UID={username};PWD={password}'
    conn_str_transdb = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database_transdb};UID={username};PWD={password}'
 
    # Connect to the MasterDB database
    conn_masterdb = pyodbc.connect(conn_str_masterdb)
    cursor_masterdb = conn_masterdb.cursor()
    
    # Connect to the TransDB database
    conn_transdb = pyodbc.connect(conn_str_transdb)
    cursor_transdb = conn_transdb.cursor()

	# Define the SELECT statement to fetch the quiz scores
    select_quizzes_query = '''
		SELECT QuizNo,Score, NoOfItems FROM QUIZ WHERE StudentNumber=? AND TeacherName=? AND SubjectName=? AND Quarter=? AND GradeLevel=?
		'''
	
	# Execute the query and fetch the results
    cursor_transdb.execute(select_quizzes_query, (student_number, teacher_name, subject_name, quarter_number,glevel))
    quizzes = cursor_transdb.fetchall()
	
	# Compute the total quiz score and total quiz items
    total_quiz_score = sum(quiz[1] for quiz in quizzes)
    total_quiz_items = sum(quiz[2] for quiz in quizzes)

	# Compute the quiz percentage
    if total_quiz_items > 0:
        quiz_percentage = (total_quiz_score / total_quiz_items) * 100
    else:
        quiz_percentage = 0
    #print('quiz_percentage = ' + str(quiz_percentage))	# quiz_percentage = 0
	
	# Convert quiz_percentage to a Decimal and round it
    quiz_percentage = Decimal(quiz_percentage).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
    quiz_percentage = quiz_percentage.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
	
	# Define the SELECT statement to fetch the formative scores
    select_formative_query = '''
		SELECT FormativeNo,Score, NoOfItems FROM FORMATIVE WHERE StudentNumber=? AND TeacherName=? AND SubjectName=? AND Quarter=? AND GradeLevel=?
		'''
	
	# Execute the query and fetch the results
    cursor_transdb.execute(select_formative_query, (student_number, teacher_name, subject_name, quarter_number,glevel))
    formative_scores = cursor_transdb.fetchall()
	
	# Compute the total formative score and total formative items
    total_formative_score = sum(formative[1] for formative in formative_scores)
    total_formative_items = sum(formative[2] for formative in formative_scores)
	
	# Compute the formative percentage
    if total_formative_items > 0:
        formative_percentage = (total_formative_score / total_formative_items) * 100
    else:
        formative_percentage = 0
    
    formative_percentage = Decimal(formative_percentage).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)	
    formative_percentage = formative_percentage.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
	
	# Define the SELECT statement to fetch the alternative scores
    select_alternative_query = '''
		SELECT AlternativeNo,Score, NoOfItems FROM ALTERNATIVE WHERE StudentNumber=? AND TeacherName=? AND SubjectName=? AND Quarter=? AND GradeLevel=?
		'''
	
	# Execute the query and fetch the results
    cursor_transdb.execute(select_alternative_query, (student_number, teacher_name, subject_name, quarter_number,glevel))
    alternative_scores = cursor_transdb.fetchall()
	
	# Compute the total alternative score and total alternative items
    total_alternative_score = sum(alternative[1] for alternative in alternative_scores)
    total_alternative_items = sum(alternative[2] for alternative in alternative_scores)
	
	# Compute the alternative percentage
    if total_alternative_items > 0:
        alternative_percentage = (total_alternative_score / total_alternative_items) * 100
    else:
        alternative_percentage = 0

    alternative_percentage = Decimal(alternative_percentage).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)	
    alternative_percentage = alternative_percentage.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
	
	# Define the SELECT statement to fetch the periodic exam scores
    select_perio_query = '''
		SELECT PerioNo,Score, NoOfItems FROM PERIO WHERE StudentNumber=? AND TeacherName=? AND SubjectName=? AND Quarter=? AND GradeLevel=?
		'''
	# Execute the query and fetch the results
    cursor_transdb.execute(select_perio_query, (student_number, teacher_name, subject_name, quarter_number,glevel))
    perio_scores = cursor_transdb.fetchall()
	
	# Compute the total perio score and total perio items
    total_perio_score = sum(perio[1] for perio in perio_scores)
    total_perio_items = sum(perio[2] for perio in perio_scores)
	
	# Compute the alternative percentage
    if total_perio_items > 0:
        perio_percentage = (total_perio_score / total_perio_items) * 100
    else:
        perio_percentage = 0
		
    perio_percentage = Decimal(perio_percentage).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)		
    perio_percentage = perio_percentage.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
		
    # Compute the overall percentage
    overall_percentage = Decimal(quiz_weight) * quiz_percentage + Decimal(formative_weight) * formative_percentage + Decimal(alternative_weight) * alternative_percentage + Decimal(perio_weight) * perio_percentage
    overall_percentage = overall_percentage.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
    #print('overall_percentage = ' + str(overall_percentage))  # result: overall_percentage = 94.90
	
	# Convert overall percentage to equivalent grade
    if overall_percentage > 95.99:
        equiv_grade = 1.00
        adjectival_equiv = 'Excellent'
    elif overall_percentage >= 90.00 and overall_percentage <= 95.99:
        equiv_grade = 1.25
        adjectival_equiv = 'Very Good'
    elif overall_percentage >= 84.00 and overall_percentage <= 85.99:
        equiv_grade = 1.50
        adjectival_equiv = 'Very Good'
    elif overall_percentage >= 78.00 and overall_percentage <= 83.99:
        equiv_grade = 1.75
        adjectival_equiv = 'Good'
    elif overall_percentage >= 72.00 and overall_percentage <= 77.99:
        equiv_grade = 2.00
        adjectival_equiv = 'Good'
    elif overall_percentage >= 66.00 and overall_percentage <= 71.99:
        equiv_grade = 2.25
        adjectival_equiv = 'Satisfactory'
    elif overall_percentage >= 60.00 and overall_percentage <= 65.99:
        equiv_grade = 2.50
        adjectival_equiv = 'Satisfactory'
    elif overall_percentage >= 55.00 and overall_percentage <= 59.99:
        equiv_grade = 2.75
        adjectival_equiv = 'Fair'
    elif overall_percentage >= 50.00 and overall_percentage <= 54.99:
        equiv_grade = 3.00
        adjectival_equiv = 'Fair'
    elif overall_percentage >= 40.00 and overall_percentage<= 49.99:
        equiv_grade = 4.00
        adjectival_equiv = 'Failed on Condition'
    elif overall_percentage < 40.00:
        equiv_grade = 5.00
        adjectival_equiv = 'Failed'
	# Close the database connection
    conn_transdb.close()

    return render_template('display_student_performance_report.html', campus_name=campus_name,
						   teacher_name=teacher_name,
						   subject_name=subject_name,
						   quiz_weight=quiz_weight,
						   formative_weight=formative_weight,
						   alternative_weight=alternative_weight,
						   perio_weight=perio_weight,
						   student_number=student_number,
                           student_name=student_name,
						   quarter_number=quarter_number,
						   quizzes=quizzes,
						   formative_scores=formative_scores,
						   alternative_scores=alternative_scores,
						   perio_scores=perio_scores,
						   quiz_percentage=quiz_percentage,
						   formative_percentage=formative_percentage,
						   alternative_percentage=alternative_percentage,
						   perio_percentage=perio_percentage,
						   overall_percentage=overall_percentage,
						   equiv_grade=equiv_grade,
						   adjectival_equiv=adjectival_equiv)

    return render_template('display_student_performance_report.html',campus=campus)
	
@app.route('/final_assessment', methods=['GET', 'POST'])
def final_assessment():
    global user_id
    global xnow
	
    from flask import Flask, render_template, request
    import pyodbc
    from decimal import Decimal, ROUND_HALF_UP

    # Replace these values with your SQL Server credentials
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database_masterdb = 'MasterDB'
    database_transdb = 'TransDB'
    username = 'sa'
    password = 'noabrir'

    # Create a connection string
    conn_str_masterdb = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database_masterdb};UID={username};PWD={password}'
    conn_str_transdb = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database_transdb};UID={username};PWD={password}'
 
    # Connect to the MasterDB database
    conn_masterdb = pyodbc.connect(conn_str_masterdb)
    cursor_masterdb = conn_masterdb.cursor()

    # Fetch the campuses from the CAMPUS table
    select_campuses_query = 'SELECT CampusName FROM CAMPUS'
    cursor_masterdb.execute(select_campuses_query)
    campuses = cursor_masterdb.fetchall()

    # Fetch the teachers from the TEACHER table
    teacher_name = request.form['teacher_name']
    select_teachers_query = 'SELECT TeacherName FROM TEACHER WHERE TeacherName=?'
    cursor_masterdb.execute(select_teachers_query,teacher_name)
    teachers = cursor_masterdb.fetchone()

    # Fetch the subjects from the SUBJECT table
    select_subjects_query = 'SELECT SubjectName,QuizWeight,FormativeWeight,AlternativeWeight,PerioWeight,TeacherName FROM SUBJECT WHERE TeacherName=?'
    cursor_masterdb.execute(select_subjects_query,teacher_name)
    #subjects = cursor_masterdb.fetchall()
    subjects = [(row[0], row[1], row[2], row[3], row[4]) for row in cursor_masterdb.fetchall()]

    # Fetch the students from the STUDENT table
    select_students_query = 'SELECT StudentNumber, FirstName, FamilyName FROM STUDENT'
    cursor_masterdb.execute(select_students_query)
    #students = cursor_masterdb.fetchall()
    students = [(row[0], row[1].strip(), row[2].strip()) for row in cursor_masterdb.fetchall()]
    student = students
 
    # Close the database connection
    conn_masterdb.close()

    return render_template('compute_index2.html', campuses=campuses, teachers=teachers, subjects=subjects, students=students,student=student)

@app.route('/display_student_performance_report2', methods=['GET', 'POST'])	
def display_student_performance_report2():
    from flask import request
    #print('request.method = ' + request.method)
    if request.method == 'POST':
        # Get the campus info from the  compute_index form
        campus_name = request.form['campus_name']
        teacher_name = request.form['teacher_name']
        subject_name = request.form['subject_name']
        quiz_weight = request.form['quiz_weight']
        formative_weight = request.form['formative_weight']
        alternative_weight = request.form['alternative_weight']
        perio_weight = request.form['perio_weight']
        glevel = request.form['glevel']
        student_number = request.form['student_number']
        student_name = request.form['student_name']
        quarter_number = request.form['quarter_number']
        student_name = student_name.upper()
		
    global user_id
    global xnow
	
    from flask import Flask, render_template, request
    import pyodbc
    from decimal import Decimal, ROUND_HALF_UP

    # Replace these values with your SQL Server credentials
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database_masterdb = 'MasterDB'
    database_transdb = 'TransDB'
    username = 'sa'
    password = 'noabrir'

    # Create a connection string
    conn_str_masterdb = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database_masterdb};UID={username};PWD={password}'
    conn_str_transdb = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database_transdb};UID={username};PWD={password}'
 
    # Connect to the MasterDB database
    conn_masterdb = pyodbc.connect(conn_str_masterdb)
    cursor_masterdb = conn_masterdb.cursor()
    
    # Connect to the TransDB database
    conn_transdb = pyodbc.connect(conn_str_transdb)
    cursor_transdb = conn_transdb.cursor()

	# Define the SELECT statement to fetch the quiz scores
    select_quizzes_query = '''
		SELECT QuizNo,Score, NoOfItems FROM QUIZ WHERE StudentNumber=? AND TeacherName=? AND SubjectName=? AND Quarter=? AND GradeLevel=?
		'''
	
	# Execute the query and fetch the results
    cursor_transdb.execute(select_quizzes_query, (student_number, teacher_name, subject_name, quarter_number,glevel))
    quizzes = cursor_transdb.fetchall()
	
	# Compute the total quiz score and total quiz items
    total_quiz_score = sum(quiz[1] for quiz in quizzes)
    total_quiz_items = sum(quiz[2] for quiz in quizzes)
	
	# Compute the quiz percentage
    if total_quiz_items > 0:
        quiz_percentage = (total_quiz_score / total_quiz_items) * 100
    else:
        quiz_percentage = 0
		
    quiz_percentage = Decimal(quiz_percentage).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)	
    quiz_percentage = quiz_percentage.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
	
	# Define the SELECT statement to fetch the formative scores
    select_formative_query = '''
		SELECT FormativeNo,Score, NoOfItems FROM FORMATIVE WHERE StudentNumber=? AND TeacherName=? AND SubjectName=? AND Quarter=? AND GradeLevel=?
		'''
	
	# Execute the query and fetch the results
    cursor_transdb.execute(select_formative_query, (student_number, teacher_name, subject_name, quarter_number, glevel))
    formative_scores = cursor_transdb.fetchall()
	
	# Compute the total formative score and total formative items
    total_formative_score = sum(formative[1] for formative in formative_scores)
    total_formative_items = sum(formative[2] for formative in formative_scores)
	
	# Compute the formative percentage
    if total_formative_items > 0:
        formative_percentage = (total_formative_score / total_formative_items) * 100
    else:
        formative_percentage = 0
		
    formative_percentage = Decimal(formative_percentage).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
    formative_percentage = formative_percentage.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
	
	# Define the SELECT statement to fetch the alternative scores
    select_alternative_query = '''
		SELECT AlternativeNo,Score, NoOfItems FROM ALTERNATIVE WHERE StudentNumber=? AND TeacherName=? AND SubjectName=? AND Quarter=? AND GradeLevel=?
		'''
	
	# Execute the query and fetch the results
    cursor_transdb.execute(select_alternative_query, (student_number, teacher_name, subject_name, quarter_number, glevel))
    alternative_scores = cursor_transdb.fetchall()
	
	# Compute the total alternative score and total alternative items
    total_alternative_score = sum(alternative[1] for alternative in alternative_scores)
    total_alternative_items = sum(alternative[2] for alternative in alternative_scores)
	
	# Compute the alternative percentage
    if total_alternative_items > 0:
        alternative_percentage = (total_alternative_score / total_alternative_items) * 100
    else:
        alternative_percentage = 0

    alternative_percentage = Decimal(alternative_percentage).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
    alternative_percentage = alternative_percentage.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
	
	# Define the SELECT statement to fetch the periodic exam scores
    select_perio_query = '''
		SELECT PerioNo,Score, NoOfItems FROM PERIO WHERE StudentNumber=? AND TeacherName=? AND SubjectName=? AND Quarter=? AND GradeLevel=?
		'''
	# Execute the query and fetch the results
    cursor_transdb.execute(select_perio_query, (student_number, teacher_name, subject_name, quarter_number, glevel))
    perio_scores = cursor_transdb.fetchall()
	
	# Compute the total perio score and total perio items
    total_perio_score = sum(perio[1] for perio in perio_scores)
    total_perio_items = sum(perio[2] for perio in perio_scores)
	
	# Compute the alternative percentage
    if total_perio_items > 0:
        perio_percentage = (total_perio_score / total_perio_items) * 100
    else:
        perio_percentage = 0
	
    perio_percentage = Decimal(perio_percentage).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)	
    perio_percentage = perio_percentage.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
		
    # Compute the overall percentage
    overall_percentage = Decimal(quiz_weight) * quiz_percentage + Decimal(formative_weight) * formative_percentage + Decimal(alternative_weight) * alternative_percentage + Decimal(perio_weight) * perio_percentage
    overall_percentage = overall_percentage.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
    #print('overall_percentage = ' + str(overall_percentage))  # result: overall_percentage = 94.90
	
    # Convert overall percentage to equivalent grade
    if overall_percentage > 95.99:
        equiv_grade = 1.00
        adjectival_equiv = 'Excellent'
    elif overall_percentage >= 90.00 and overall_percentage <= 95.99:
        equiv_grade = 1.25
        adjectival_equiv = 'Very Good'
    elif overall_percentage >= 84.00 and overall_percentage <= 85.99:
        equiv_grade = 1.50
        adjectival_equiv = 'Very Good'
    elif overall_percentage >= 78.00 and overall_percentage <= 83.99:
        equiv_grade = 1.75
        adjectival_equiv = 'Good'
    elif overall_percentage >= 72.00 and overall_percentage <= 77.99:
        equiv_grade = 2.00
        adjectival_equiv = 'Good'
    elif overall_percentage >= 66.00 and overall_percentage <= 71.99:
        equiv_grade = 2.25
        adjectival_equiv = 'Satisfactory'
    elif overall_percentage >= 60.00 and overall_percentage <= 65.99:
        equiv_grade = 2.50
        adjectival_equiv = 'Satisfactory'
    elif overall_percentage >= 55.00 and overall_percentage <= 59.99:
        equiv_grade = 2.75
        adjectival_equiv = 'Fair'
    elif overall_percentage >= 50.00 and overall_percentage <= 54.99:
        equiv_grade = 3.00
        adjectival_equiv = 'Fair'
    elif overall_percentage >= 40.00 and overall_percentage<= 49.99:
        equiv_grade = 4.00
        adjectival_equiv = 'Failed on Condition'
    elif overall_percentage < 40.00:
        equiv_grade = 5.00
        adjectival_equiv = 'Failed'
	# Close the database connection
    conn_transdb.close()

    return render_template('display_student_performance_report2.html', campus_name=campus_name,
						   teacher_name=teacher_name,
						   subject_name=subject_name,
						   quiz_weight=quiz_weight,
						   formative_weight=formative_weight,
						   alternative_weight=alternative_weight,
						   perio_weight=perio_weight,
						   student_number=student_number,
                           student_name=student_name,
						   quarter_number=quarter_number,
						   quizzes=quizzes,
						   formative_scores=formative_scores,
						   alternative_scores=alternative_scores,
						   perio_scores=perio_scores,
						   quiz_percentage=quiz_percentage,
						   formative_percentage=formative_percentage,
						   alternative_percentage=alternative_percentage,
						   perio_percentage=perio_percentage,
						   overall_percentage=overall_percentage,
						   equiv_grade=equiv_grade,
						   adjectival_equiv=adjectival_equiv)

    return render_template('display_student_performance_report2.html',campus=campus)
	
	
# STUDENT QUARTERLY REPORT CARD
@app.route('/')  
@app.route('/select_student/')
def select_student():
    global user_id
    global xnow
    cursor = conn.cursor()
	
    select_students_query = 'SELECT StudentNumber,FirstName,FamilyName FROM STUDENT'
    cursor_masterdb.execute(select_students_query)
    students = [(row[0].strip(),row[1].strip(),row[2].strip()) for row in cursor_masterdb.fetchall()]
    students = students
    #print(students)
    '''
    [('12-001', 'VIBIEN', 'CONTI'), 
	('20-120145', 'VINCENT II', 'CONTI'), 
	('9-001', 'F', 'G'), 
	('PROF-001', 'VIRGILO', 'CONTI'), 
	('PROF-002', 'A', 'B'), 
	('PROF-003', 'X', 'Y'), 
	('PROF-004', 'X', 'Y'), 
	('PROF-005', 'X', 'Y'), 
	('PROF-006', 'X', 'Y')]
    '''
    return render_template('select_student.html',students=students)
	
@app.route('/quarterly_reportcard', methods=['GET', 'POST'])	
def quarterly_reportcard():
    global user_id
    global xnow
    print('user_id = ' + str(user_id))   # user_id = 20-120145-P
    print('xnow = ' + str(xnow))    # xnow = 2023-08-07 10:41:49.111265
	
    student_number = request.form['student_number']   # user_id = 20-120145-P
    student_name = request.form['student_name']
	
    print('student_number = ' + str(student_number))   # user_id = 20-120145-P
    print('student_name = ' + student_name)    # student_name = VINCENT II CONTI
    return 'quarterly_reportcard() successfully accessed.'    # quarterly_reportcard() successfully accessed.
	
    from flask import Flask, render_template, request
    import pyodbc
    from decimal import Decimal, ROUND_HALF_UP
	
    import string
    from datetime import datetime
    #from jinja2 import Template

    from flask import Flask, render_template, request
    from flask_cors import CORS
    
    from asgiref.wsgi import WsgiToAsgi
    from hypercorn.config import Config
    from hypercorn.asyncio import serve

    import sys
    from string import Template



#print(__name__)      # __name__  = __main__
    app = Flask(__name__)

    CORS(app)  # Enable Cross-origin resource sharing

    # Replace these values with your SQL Server credentials
    server = 'DESKTOP-CUSCHDO\SQLEXPRESS'
    database_masterdb = 'MasterDB'
    database_transdb = 'TransDB'
    username = 'sa'
    password = 'noabrir'

    # Create a connection string
    conn_str_masterdb = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database_masterdb};UID={username};PWD={password}'
    conn_str_transdb = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database_transdb};UID={username};PWD={password}'
 
    # Connect to the MasterDB database
    conn_masterdb = pyodbc.connect(conn_str_masterdb)
    cursor_masterdb = conn_masterdb.cursor()
    
    # Connect to the TransDB database
    conn_transdb = pyodbc.connect(conn_str_transdb)
    cursor_transdb = conn_transdb.cursor()
    '''
    cursor.execute("SELECT * FROM RCARDHEADER WHERE StudentNumber=?", student_number)
    rows = cursor_transdb.fetchall()
	
    cursor.execute("SELECT * FROM REPORTCARD WHERE StudentNumber=?", student_number)
    rows2 = cursor_transdb.fetchall()
    '''	
	
	# Retrieve the report card header
    cursor_transdb.execute("SELECT StudentName, YearAndSection, SchoolYear, Age, Sex, Campus, AdviserCommentsFeedback FROM RCARDHEADER WHERE StudentNumber = ?", student_number)
    header = cursor.fetchone()

	# Retrieve the report card details
    cursor_transdb.execute("SELECT SubjectCode, Course, Description, Quarter1Grade, Quarter2Grade, Quarter3Grade, Quarter4Grade, FinalGrade, Credit FROM REPORTCARD WHERE StudentNumber = ?", student_number)
    details = cursor.fetchall()

	# Compute the quarterly and final weighted average grade
    quarter1_sum = 0
    quarter2_sum = 0
    quarter3_sum = 0
    quarter4_sum = 0
    final_sum = 0
    total_credits = 0

    for row in details:
	    quarter1_sum += row.Quarter1Grade * row.Credit
	    quarter2_sum += row.Quarter2Grade * row.Credit
	    quarter3_sum += row.Quarter3Grade * row.Credit
	    quarter4_sum += row.Quarter4Grade * row.Credit
	    final_sum += row.FinalGrade * row.Credit
	    total_credits += row.Credit

    quarter1_avg = quarter1_sum / total_credits
    quarter2_avg = quarter2_sum / total_credits
    quarter3_avg = quarter3_sum / total_credits
    quarter4_avg = quarter4_sum / total_credits
    final_avg = final_sum / total_credits

	# Close the database connection
    #conn_transdb.close()

# Generate HTML report
html_template = '''	
<!DOCTYPE html>
<html>
<head>
    <style>
        table {
            border-collapse: collapse;
            width: 100%;
        }
        th, td {
            border: 1px solid black;
            padding: 8px;
            text-align: center;
        }
        tr:nth-child(even) {background-color: #f2f2f2;}
        th {
            background-color: #4CAF50;
            color: white;
        }
    </style>
</head>
<body>

<h2>Final Report Card</h2>

<h3>Report Card Header</h3>
<table>
    <tr>
        <th>Student Name</th>
        <th>Year and Section</th>
        <th>School Year</th>
        <th>Age</th>
        <th>Sex</th>
        <th>Campus</th>
        <th>Adviser Comments/Feedback</th>
    </tr>
    <tr>
        <td>${ header.StudentName }</td>
        <td>${ header.YearAndSection }</td>
        <td>${ header.SchoolYear }</td>
        <td>${ header.Age }</td>
        <td>${ header.Sex }</td>
        <td>${ header.Campus }</td>
        <td>${ header.AdviserCommentsFeedback }</td>
    </tr>
</table>

<h3>Report Card Details</h3>
<table>
    <tr>
        <th>Subject Code</th>
        <th>Course</th>
        <th>Description</th>
        <th>Quarter 1 Grade</th>
        <th>Quarter 2 Grade</th>
        <th>Quarter 3 Grade</th>
        <th>Quarter 4 Grade</th>
        <th>Final Grade</th>
        <th>Credit</th>
    </tr>

    <!--{% for row in details %}-->
	$for row in details:
    <tr>
        <td>${ row.SubjectCode }</td>
        <td>${ row.Course }</td>
        <td>${ row.Description }</td>
        <td>${ row.Quarter1Grade }</td>
        <td>${ row.Quarter2Grade }</td>
        <td>${ row.Quarter3Grade }</td>
        <td>${ row.Quarter4Grade }</td>
	</tr>
</table>
</body>
</html>
'''

# Create HTML report (perio_report.html) using Jinja2 template
template = Template(html_template)
html_report = template.render(header=header, details=details)

# Save HTML report to a file
report_file = 'report_card.html'
with open(report_file, 'w') as f:
    f.write(html_report)

import webbrowser
webbrowser.open('report_card.html')

# Close database connection
cursor_transdb.close()
conn_transdb.close()


if __name__ == '__main__':
    #app.run()
    app.run(debug=True)
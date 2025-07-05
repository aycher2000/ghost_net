from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/school.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Association table for Student-Course relationship (Many-to-Many)
enrollments = db.Table('enrollments',
    db.Column('student_id', db.Integer, db.ForeignKey('student.id')),
    db.Column('course_id', db.Integer, db.ForeignKey('course.id')),
    db.Column('enrollment_date', db.DateTime, default=datetime.utcnow)
)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    # One-to-One relationship with StudentProfile
    profile = db.relationship('StudentProfile', backref='student', uselist=False)
    # Many-to-Many relationship with Course
    courses = db.relationship('Course', secondary=enrollments, backref='students')
    # One-to-Many relationship with Grade
    grades = db.relationship('Grade', backref='student')

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'profile': self.profile.to_dict() if self.profile else None,
            'courses': [course.to_dict() for course in self.courses]
        }

class StudentProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), unique=True)
    date_of_birth = db.Column(db.Date)
    address = db.Column(db.String(200))
    phone = db.Column(db.String(20))

    def to_dict(self):
        return {
            'id': self.id,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'address': self.address,
            'phone': self.phone
        }

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    # One-to-Many relationship with Course
    courses = db.relationship('Course', backref='teacher')

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'courses': [course.to_dict() for course in self.courses]
        }

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
    # One-to-Many relationship with Grade
    grades = db.relationship('Grade', backref='course')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'teacher_id': self.teacher_id
        }

class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    grade = db.Column(db.Float, nullable=False)
    date_received = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'course_id': self.course_id,
            'grade': self.grade,
            'date_received': self.date_received.isoformat()
        }

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)
    mac_address = db.Column(db.String(17), nullable=False)
    device_type = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    owner = db.Column(db.String(100), nullable=False)
    notes = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'hostname': self.hostname,
            'ip_address': self.ip_address,
            'mac_address': self.mac_address,
            'device_type': self.device_type,
            'location': self.location,
            'owner': self.owner,
            'notes': self.notes
        }

# Create the database tables
with app.app_context():
    db.create_all()

# API Routes

@app.route('/')
def home():
    return '''
    <h1>School Management System API</h1>
    <h2>Available Endpoints:</h2>
    <h3>Students</h3>
    <ul>
        <li><b>GET /students</b> - List all students</li>
        <li><b>POST /students</b> - Create a new student
            <br>Required data: {"first_name": "string", "last_name": "string", "email": "string"}
        </li>
        <li><b>POST /students/{id}/profile</b> - Add profile for a student
            <br>Required data: {"date_of_birth": "YYYY-MM-DD", "address": "string", "phone": "string"}
        </li>
        <li><b>GET /students/{id}/grades</b> - Get student's grades</li>
    </ul>

    <h3>Teachers</h3>
    <ul>
        <li><b>GET /teachers</b> - List all teachers</li>
        <li><b>POST /teachers</b> - Create a new teacher
            <br>Required data: {"first_name": "string", "last_name": "string", "email": "string"}
        </li>
    </ul>

    <h3>Courses</h3>
    <ul>
        <li><b>GET /courses</b> - List all courses</li>
        <li><b>POST /courses</b> - Create a new course
            <br>Required data: {"name": "string", "description": "string", "teacher_id": number}
        </li>
    </ul>

    <h3>Enrollments & Grades</h3>
    <ul>
        <li><b>POST /students/{student_id}/enroll/{course_id}</b> - Enroll student in a course</li>
        <li><b>POST /grades</b> - Add a grade
            <br>Required data: {"student_id": number, "course_id": number, "grade": number}
        </li>
    </ul>

    <h3>Devices</h3>
    <ul>
        <li><b>POST /devices</b> - Create a new device</li>
        <li><b>GET /devices</b> - List all devices</li>
        <li><b>GET /devices/{id}</b> - Get a specific device</li>
        <li><b>PUT /devices/{id}</b> - Update a device</li>
        <li><b>DELETE /devices/{id}</b> - Delete a device</li>
    </ul>

    <h3>Example Usage:</h3>
    <pre>
    # Create a teacher
    curl -X POST http://localhost:5000/teachers \\
      -H "Content-Type: application/json" \\
      -d '{
        "first_name": "John",
        "last_name": "Smith",
        "email": "john.smith@school.com"
      }'

    # Create a course
    curl -X POST http://localhost:5000/courses \\
      -H "Content-Type: application/json" \\
      -d '{
        "name": "Introduction to Python",
        "description": "Learn Python basics",
        "teacher_id": 1
      }'

    # Create a student
    curl -X POST http://localhost:5000/students \\
      -H "Content-Type: application/json" \\
      -d '{
        "first_name": "Alice",
        "last_name": "Johnson",
        "email": "alice.j@student.com"
      }'
    </pre>
    '''

@app.route('/students', methods=['POST'])
def create_student():
    data = request.get_json()
    new_student = Student(
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email']
    )
    db.session.add(new_student)
    db.session.commit()
    return jsonify(new_student.to_dict()), 201

@app.route('/students/<int:id>/profile', methods=['POST'])
def add_student_profile(id):
    student = Student.query.get_or_404(id)
    data = request.get_json()
    profile = StudentProfile(
        student_id=student.id,
        date_of_birth=datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date(),
        address=data['address'],
        phone=data['phone']
    )
    db.session.add(profile)
    db.session.commit()
    return jsonify(profile.to_dict()), 201

@app.route('/teachers', methods=['POST'])
def create_teacher():
    data = request.get_json()
    new_teacher = Teacher(
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email']
    )
    db.session.add(new_teacher)
    db.session.commit()
    return jsonify(new_teacher.to_dict()), 201

@app.route('/teachers/<int:id>', methods=['DELETE'])
def delete_teacher(id):
    teacher = Teacher.query.get_or_404(id)
    db.session.delete(teacher)
    db.session.commit()
    return jsonify({'message': f'Teacher {id} deleted.'}), 200

@app.route('/courses', methods=['POST'])
def create_course():
    data = request.get_json()
    new_course = Course(
        name=data['name'],
        description=data['description'],
        teacher_id=data['teacher_id']
    )
    db.session.add(new_course)
    db.session.commit()
    return jsonify(new_course.to_dict()), 201

@app.route('/students/<int:student_id>/enroll/<int:course_id>', methods=['POST'])
def enroll_student(student_id, course_id):
    student = Student.query.get_or_404(student_id)
    course = Course.query.get_or_404(course_id)
    student.courses.append(course)
    db.session.commit()
    return jsonify({'message': 'Student enrolled successfully'}), 200

@app.route('/grades', methods=['POST'])
def add_grade():
    data = request.get_json()
    new_grade = Grade(
        student_id=data['student_id'],
        course_id=data['course_id'],
        grade=data['grade']
    )
    db.session.add(new_grade)
    db.session.commit()
    return jsonify(new_grade.to_dict()), 201

@app.route('/devices', methods=['POST'])
def create_device():
    data = request.get_json()
    device = Device(
        hostname=data['hostname'],
        ip_address=data['ip_address'],
        mac_address=data['mac_address'],
        device_type=data['device_type'],
        location=data['location'],
        owner=data['owner'],
        notes=data.get('notes')
    )
    db.session.add(device)
    db.session.commit()
    return jsonify(device.to_dict()), 201

@app.route('/devices', methods=['GET'])
def list_devices():
    devices = Device.query.all()
    return jsonify([d.to_dict() for d in devices])

@app.route('/devices/<int:id>', methods=['GET'])
def get_device(id):
    device = Device.query.get_or_404(id)
    return jsonify(device.to_dict())

@app.route('/devices/<int:id>', methods=['PUT'])
def update_device(id):
    device = Device.query.get_or_404(id)
    data = request.get_json()
    device.hostname = data.get('hostname', device.hostname)
    device.ip_address = data.get('ip_address', device.ip_address)
    device.mac_address = data.get('mac_address', device.mac_address)
    device.device_type = data.get('device_type', device.device_type)
    device.location = data.get('location', device.location)
    device.owner = data.get('owner', device.owner)
    device.notes = data.get('notes', device.notes)
    db.session.commit()
    return jsonify(device.to_dict())

@app.route('/devices/<int:id>', methods=['DELETE'])
def delete_device(id):
    device = Device.query.get_or_404(id)
    db.session.delete(device)
    db.session.commit()
    return jsonify({'message': f'Device {id} deleted.'}), 200

@app.route('/students', methods=['GET'])
def get_students():
    students = Student.query.all()
    return jsonify([student.to_dict() for student in students])

@app.route('/teachers', methods=['GET'])
def get_teachers():
    teachers = Teacher.query.all()
    return jsonify([teacher.to_dict() for teacher in teachers])

@app.route('/courses', methods=['GET'])
def get_courses():
    courses = Course.query.all()
    return jsonify([course.to_dict() for course in courses])

@app.route('/students/<int:id>/grades', methods=['GET'])
def get_student_grades(id):
    student = Student.query.get_or_404(id)
    return jsonify([grade.to_dict() for grade in student.grades])

@app.route('/dashboard', methods=['GET'])
def dashboard():
    devices = Device.query.all()
    return render_template('dashboard.html', devices=devices)

@app.route('/dashboard/add', methods=['POST'])
def dashboard_add():
    data = request.form
    device = Device(
        hostname=data['hostname'],
        ip_address=data['ip_address'],
        mac_address=data['mac_address'],
        device_type=data['device_type'],
        location=data['location'],
        owner=data['owner'],
        notes=data.get('notes')
    )
    db.session.add(device)
    db.session.commit()
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 
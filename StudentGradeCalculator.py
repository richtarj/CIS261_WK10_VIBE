#!/usr/bin/env python3
import os
import sys

FILENAME = 'student_grades.txt'

def getch():
    """Read a single character from stdin (Unix)."""
    try:
        import tty, termios
    except ImportError:
        # Fallback for non-Unix (very rare here)
        return sys.stdin.read(1)
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
    return ch


class Student:
    def __init__(self, name: str, sid: str, test1: float, test2: float, test3: float):
        self.name = name.strip()
        self.id = sid.strip()
        self.test1 = float(test1)
        self.test2 = float(test2)
        self.test3 = float(test3)
        self.average = self.calculate_average()
        self.grade = self.calculate_grade()

    def calculate_average(self) -> float:
        return round((self.test1 + self.test2 + self.test3) / 3.0, 2)

    def calculate_grade(self) -> str:
        a = self.average
        if a >= 90:
            return 'A'
        if a >= 80:
            return 'B'
        if a >= 70:
            return 'C'
        if a >= 60:
            return 'D'
        return 'F'

    def to_record(self) -> str:
        return f"{self.name}|{self.id}|{self.test1:.2f}|{self.test2:.2f}|{self.test3:.2f}|{self.average:.2f}|{self.grade}"

    @classmethod
    def from_record(cls, line: str):
        parts = line.strip().split('|')
        if len(parts) < 7:
            raise ValueError('Invalid record format')
        name, sid, t1, t2, t3, avg, grade = parts[:7]
        return cls(name, sid, float(t1), float(t2), float(t3))


def load_records() -> list:
    students = []
    if not os.path.exists(FILENAME):
        return students
    try:
        with open(FILENAME, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    s = Student.from_record(line)
                    students.append(s)
                except Exception:
                    print(f"Warning: skipping invalid line: {line}")
    except Exception as e:
        print(f"Error loading {FILENAME}: {e}")
    return students


def save_records(students: list):
    try:
        with open(FILENAME, 'w') as f:
            for s in students:
                f.write(s.to_record() + '\n')
        print(f"Saved {len(students)} record(s) to {FILENAME}.")
    except Exception as e:
        print(f"Error saving to {FILENAME}: {e}")


def display_students(students: list):
    if not students:
        print("No student records to display.")
        return
    hdr = f"{'Name':<20} {'ID':<10} {'Test1':>7} {'Test2':>7} {'Test3':>7} {'Average':>8} {'Grade':>6}"
    print(hdr)
    print('-' * len(hdr))
    for s in students:
        print(f"{s.name:<20} {s.id:<10} {s.test1:7.2f} {s.test2:7.2f} {s.test3:7.2f} {s.average:8.2f} {s.grade:6}")


def class_statistics(students: list):
    if not students:
        print("No student records for statistics.")
        return
    averages = [s.average for s in students]
    highest = max(averages)
    lowest = min(averages)
    class_avg = round(sum(averages) / len(averages), 2)
    print(f"Highest average: {highest:.2f}")
    print(f"Lowest average: {lowest:.2f}")
    print(f"Class average: {class_avg:.2f}")


def search_student(students: list):
    name = input('Enter student name to search (case-insensitive): ').strip()
    if not name:
        print('Empty search term.')
        return
    term = name.lower()
    matches = [s for s in students if term in s.name.lower()]
    if not matches:
        print('No matching students found.')
        return
    display_students(matches)


def add_student(students: list):
    print('Add new student (type ESC to cancel at any prompt by entering ESC).')
    name = input('Name: ').strip()
    if name.upper() == 'ESC' or name == '':
        print('Add cancelled.')
        return
    sid = input('Student ID: ').strip()
    if sid.upper() == 'ESC' or sid == '':
        print('Add cancelled.')
        return
    def read_score(prompt):
        while True:
            val = input(prompt).strip()
            if val.upper() == 'ESC':
                return None
            try:
                f = float(val)
                if f < 0 or f > 100:
                    print('Score must be between 0 and 100.')
                    continue
                return f
            except ValueError:
                print('Please enter a valid number (0-100) or ESC to cancel.')

    t1 = read_score('Test 1 score: ')
    if t1 is None:
        print('Add cancelled.')
        return
    t2 = read_score('Test 2 score: ')
    if t2 is None:
        print('Add cancelled.')
        return
    t3 = read_score('Test 3 score: ')
    if t3 is None:
        print('Add cancelled.')
        return

    student = Student(name, sid, t1, t2, t3)
    students.append(student)
    print(f"Student '{student.name}' added with average {student.average:.2f} and grade {student.grade}.")


def main():
    students = load_records()
    print(f"Loaded {len(students)} record(s) from {FILENAME}.")

    menu = (
        "\nStudent Grade Calculator - Menu:\n"
        "1 - Add new student\n"
        "2 - Display all students\n"
        "3 - Class statistics\n"
        "4 - Search student by name\n"
        "5 - Save records\n"
        "Press ESC to exit\n"
    )

    while True:
        print(menu)
        print('Choose an option (press the digit key).')
        ch = getch()
        if ch == '\x1b':  # ESC
            print('\nExiting program...')
            save_records(students)
            break
        if ch == '1':
            print()
            add_student(students)
        elif ch == '2':
            print()
            display_students(students)
        elif ch == '3':
            print()
            class_statistics(students)
        elif ch == '4':
            print()
            search_student(students)
        elif ch == '5':
            print()
            save_records(students)
        else:
            print('\nInvalid choice. Please press a menu digit or ESC to exit.')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nInterrupted. Saving records...')
        try:
            save_records(globals().get('students', []))
        except Exception:
            pass
        print('Goodbye.')

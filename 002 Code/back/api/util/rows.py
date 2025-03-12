import pandas as pd
from api.models import ExceptionCourseOffer, FatherCourseOffer, ChildCourseOffer, AssignTable, NotGeneratedCourseTable, \
    NotGeneratedResourceTable


def add_exception_row(row: pd.Series):
    exception_row = ExceptionCourseOffer(
        CourseCode=row['CourseCode'],
        FacultyCode=row['FacultyCode'],
        Session=row['Session'],
        Capacity=row['Capacity'],
        MinPerSession=row['Min Per Session'],
        Lecturer=row['Lecturer'],
    )

    exception_row.save()

def add_father_row(row: pd.Series):
    father_row = FatherCourseOffer(
        CourseCode=row['CourseCode'],
        FacultyCode=row['FacultyCode'],
        Session=row['Session'],
        Capacity=row['Capacity'],
        MinPerSession=row['Min Per Session'],
        Lecturer=row['Lecturer'],
        CourseType=row['CourseType'],
    )

    father_row.save()

def add_child_row(row: pd.Series):

    child_row = ChildCourseOffer(
        FatherCode=row['FacultyCode'],
        CourseCode=row['CourseCode'],
        Capacity=row['Capacity'],
    )
    child_row.save()

def add_assign_row(row: pd.Series):
    assign_row = AssignTable(
        CourseCode=row['coursecode'],
        ResourceCode=row['room'],
        FacultyCode=row['facultyCode'],
        Session=row['session'],
        Lecturer=row['professor'],
        CourseCapacity=row['capacity'],
        RoomCapacity=row['room_capacity'],
        DayOfWeek=row['day'],
        StartTime=row['start_time'],
        MinPerSession=row['MinPerSession'],
    )

    assign_row.save()

def add_ng_course_row(row: pd.Series):
    row = NotGeneratedCourseTable(
        CourseCode=row['coursecode'],
        FacultyCode=row['facultyCode'],
        Capacity=row['capacity'],
        MinPerSession=row['MinPerSession'],
        Lecturer=row['professor'],
    )

    row.save()

def add_ng_resource_row(row: pd.Series):
    row = NotGeneratedResourceTable(
        ResourceCode=row['ResourceCode'],
        Description=row['Description'],
        Capacity=row['Capacity'],
        Lecture=row['Lecture'],
        Tutorial=row['Tutorial'],
        Lab=row['Lab'],
        ETC=row['ETC'],
    )

    row.save()
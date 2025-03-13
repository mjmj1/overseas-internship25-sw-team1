import pandas as pd
import os
from django.conf import settings
from .rows import add_exception_row
from ..models import FatherCourseOffer, ChildCourseOffer

COURSEOFFERPATH = 'CSD - Course Offer.xlsx'

def make_course_tables():
    file_path = os.path.join(settings.BASE_DIR, 'datas', COURSEOFFERPATH)
    if not os.path.exists(file_path):
        print("파일이 존재하지 않습니다.")
        return

    df = pd.read_excel(file_path)

    df = df.drop(df.tail(1).index).drop(columns=['Unnamed: 0'])

    df = add_check_code(df)
    df = del_only_combined_to(df)
    df = del_self_reference(df)

    make_family_tables(df)


def add_check_code(df):
    df['check_code'] = df['Session'].apply(
        lambda x:
        "Only Combined To" if isinstance(x, str) and x.strip() == "Combined To /"
        else x.split('Combined To ')[-1].split('/', 1)[0] if isinstance(x, str) and 'Combined To' in x
        else None
    )
    df['FatherCode'] = None

    return df


def del_only_combined_to(df):
    drop_list = []

    for index, row in df.iterrows():
        if row['check_code'] == "Only Combined To":
            drop_list.append(index)
            add_exception_row(row)

    df = df.drop(drop_list).reset_index(drop=True)

    return df


def del_self_reference(df):
    drop_list = []

    for index, row in df.iterrows():
        if row['check_code'] == row['CourseCode']:
            drop_list.append(index)
            add_exception_row(row)

    df = df.drop(drop_list).reset_index(drop=True)

    return df


def make_family_tables(df):
    father_df, child_df = separate_table(df)
    child_df = check_father_code(father_df, child_df)
    child_df = check_child_code(child_df)
    child_df = check_exception_df(child_df)
    father_df = make_courseType_fatherCode(father_df)

    objects = [
        FatherCourseOffer(
            CourseCode=row['CourseCode'],
            FacultyCode=row['FacultyCode'],
            Session=row['Session'],
            Capacity=row['Capacity'],
            MinPerSession=row['Min Per Session'],
            Lecturer=row['Lecturer'],
            CourseType=row['CourseType'],
        )
        for _, row in father_df.iterrows()
    ]

    FatherCourseOffer.objects.bulk_create(objects, ignore_conflicts=True)

    objects = [
        ChildCourseOffer(
            FatherCode=row['FatherCode'],
            CourseCode=row['CourseCode'],
            Capacity=row['Capacity'],
            Session=row['Session'],
        )
        for _, row in child_df.iterrows()
    ]

    ChildCourseOffer.objects.bulk_create(objects, ignore_conflicts=True)


def separate_table(df):
    father_list = []
    child_list = []

    for index, row in df.iterrows():
        if row['check_code'] is None:
            father_list.append(row)
        else:
            child_list.append(row)

    father_df = pd.DataFrame(father_list)
    child_df = pd.DataFrame(child_list)

    father_df.drop(columns=['check_code', 'FatherCode'], inplace=True)

    return father_df, child_df


def check_father_code(father_df, child_df):
    for index, row in child_df.iterrows():
        if row['check_code'] in father_df['CourseCode'].values:
            father_code = father_df.loc[father_df['CourseCode'] == row['check_code'], 'CourseCode'].values[0]
            child_df.at[index, 'FatherCode'] = father_code

    return child_df


def check_child_code(child_df):
    for index, row in child_df.iterrows():
        if row['check_code'] in child_df['CourseCode'].values:
            new_father_code = child_df.loc[child_df['CourseCode'] == row['check_code'], 'FatherCode'].values[0]
            child_df.at[index, 'FatherCode'] = new_father_code

    return child_df

def check_exception_df(child_df):
    drop_list = []

    for index, row in child_df.iterrows():
        if pd.isna(row['FatherCode']):
            add_exception_row(row)
            drop_list.append(index)

    child_df = child_df.drop(drop_list).reset_index(drop=True)

    return child_df

def make_courseType_fatherCode(df):
    mapping = {
        'Lecture': 'Le',
        'Tutorial': 'Tu',
        'Group': 'Gr',
        'Clinic': 'Cl',
        'LAB': 'La',
        'Lab': 'La',
        'PBL': 'PB',
        'Kitchen': 'Ki',
        'Drawing': 'Dr'
    }

    df['CourseType'] = df['Session'].apply(
        lambda x: next((value for key, value in mapping.items() if isinstance(x, str) and key in x), '')
    )

    return df

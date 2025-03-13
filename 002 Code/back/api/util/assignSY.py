import random
import pandas as pd
import numpy as np
import math

from api.models import FatherCourseOffer, ChildCourseOffer
from api.util.assignTT import get_father_course_data, get_resource_room_data, get_child_course_data
from api.util.rows import add_assign_row


def split_min_per_session(df):
    new_rows = []  # 나뉜 데이터를 저장할 리스트
    split_id_counter = 1  # Split ID 증가용 카운터

    for idx, row in df.iterrows():
        min_per_session = row["MinPerSession"]
        if min_per_session > 180:
            split_label = str(split_id_counter)  # split_id 할당
            split_id_counter += 1
        else:
            split_label = "N"  # 분할되지 않으면 "N"

        first_split = True  # 첫 번째 행인지 확인
        while min_per_session > 180:
            new_row = row.copy()  # 기존 행 복사
            new_row["MinPerSession"] = 180  # 180으로 자른 값 추가
            new_row["Split"] = "Y"  # Split 여부
            new_row["Split_ID"] = split_label  # Split ID 추가
            new_rows.append(new_row)  # 새로운 행 추가
            min_per_session -= 180  # 남은 시간 줄이기
            first_split = False  # 이후 행들은 부모가 아님

        # 마지막 남은 시간을 추가
        new_row = row.copy()
        new_row["MinPerSession"] = min_per_session
        new_row["Split"] = "Y" if not first_split else "N"
        new_row["Split_ID"] = split_label
        new_rows.append(new_row)

    return pd.DataFrame(new_rows).reset_index(drop=True)

def initialize_population(size, course_df, days, times):
    population = []

    for _ in range(size):
        timetable = []
        professor_schedule = {}  # 교수별 배정된 시간 저장 (교수 ID -> (요일, 시간) 리스트)
        split_schedule = {}  # Split_ID별 배정된 시간 저장

        for _, lecture in course_df.iterrows():
            professor = lecture["Lecturer"]
            split_id = lecture["Split_ID"] if lecture["Split"] == "Y" else None
            session_duration = lecture['MinPerSession'] / 60  # 분 단위를 시간 단위로 변환

            if professor not in professor_schedule:
                professor_schedule[professor] = []
            if split_id and split_id not in split_schedule:
                split_schedule[split_id] = []

            # 가능한 시간 슬롯 필터링 (교수와 Split_ID 중복 확인)
            available_slots = [(d, t) for d in days for t in times
                               if (d, t) not in professor_schedule[professor]
                               and (not split_id or (d, t) not in split_schedule[split_id])
                               and (t + session_duration <= 22)]  # 22시 초과 방지

            if not available_slots:
                print(f"❌ No available slots for {lecture['CourseCode']} - Skipping")
                continue

            new_day, new_time = random.choice(available_slots)  # 충돌 없는 시간 선택

            # 시간표에 추가
            timetable.append({
                'coursecode': lecture['CourseCode'],
                'facultyCode': lecture['FacultyCode'],
                'session': lecture['Session'],
                'professor': professor,
                'capacity': lecture['Capacity'],
                'CourseType': lecture['CourseType'],
                'day': new_day,
                'split_id': split_id,
                'start_time': new_time,
                'end_time': new_time + session_duration,  # 종료 시간이 22시 이하로 유지됨
                'MinPerSession': session_duration,
                'CombineBy': '',
            })

            # 교수 및 Split_ID 스케줄 업데이트
            professor_schedule[professor].append((new_day, new_time))
            if split_id:
                split_schedule[split_id].append((new_day, new_time))

        timetable = pd.DataFrame(timetable)
        population.append(timetable)

    return population

def assign_rooms(timetable_df, rooms_df):
    assigned_rooms = []  # (day, room_name, start_time, end_time) 형태로 저장
    updated_timetable = []
    unassigned_lectures = []

    for idx, lecture in timetable_df.iterrows():
        capacity_needed = lecture['capacity']
        day, start_time, end_time = lecture['day'], lecture['start_time'], lecture['end_time']
        course_type = lecture['CourseType']  # 강의 유형

        # 강의 유형에 맞는 강의실 필터링
        if course_type == 'Le':  # Lecture
            available_rooms = rooms_df[(rooms_df['Capacity'] >= capacity_needed) & (rooms_df['Lecture'] == 'Y')]
        elif course_type == 'La':  # Lab
            available_rooms = rooms_df[(rooms_df['Capacity'] >= capacity_needed) & (rooms_df['Lab'] == 'Y')]
        elif course_type == 'Tu':  # Tutorial
            available_rooms = rooms_df[(rooms_df['Capacity'] >= capacity_needed) & (rooms_df['Tutorial'] == 'Y')]
        elif course_type == 'Gr' or course_type == 'Cl' or course_type == 'PB' or course_type == 'Ki' or course_type == 'Dr':  # Group
            available_rooms = rooms_df[(rooms_df['Capacity'] >= capacity_needed) & (rooms_df['ETC'] == 'Y')]
        else:
            available_rooms = rooms_df[rooms_df['Capacity'] >= capacity_needed]

        if available_rooms.empty:
            unassigned_lectures.append(lecture)
        else:
            available_rooms = available_rooms.sample(frac=1).reset_index(drop=True)
            selected_room = available_rooms.iloc[0]
            room_name = selected_room['ResourceCode']
            room_capacity = selected_room['Capacity']
            assigned_rooms.append((day, room_name, start_time, end_time))
            updated_timetable.append({
                **lecture,
                'room': room_name,
                'room_capacity': room_capacity
            })

    # 남은 강의 배정 시도
    for lecture in unassigned_lectures:
        capacity_needed = lecture['capacity']
        available_rooms = rooms_df[rooms_df['Capacity'] >= capacity_needed]
        if available_rooms.empty:
            print(f"  ❌ Still No Room Available for {lecture['coursecode']} - Skipping")
        else:
            available_rooms = available_rooms.sample(frac=1).reset_index(drop=True)
            selected_room = available_rooms.iloc[0]
            room_name = selected_room['ResourceCode']
            room_capacity = selected_room['Capacity']
            updated_timetable.append({
                **lecture,
                'room': room_name,
                'room_capacity': room_capacity
            })

    return pd.DataFrame(updated_timetable)

def generate_timetable(course_df, rooms_df, days, times):
    population = initialize_population(100, course_df, days, times)
    print("✅ Population initialized successfully!")

    assigned_population = [assign_rooms(timetable, rooms_df) for timetable in population]
    print("✅ Rooms assigned successfully!")

    results = []
    for timetable in assigned_population:
        all_rooms = set(rooms_df['ResourceCode'])
        assigned_rooms = set(timetable['room'].dropna())
        unused_rooms = all_rooms - assigned_rooms
        unassigned_courses = timetable[timetable['room'].isna()]

        results.append((timetable, unused_rooms, unassigned_courses))

    print("✅ Timetable generation completed successfully!")
    return results

def make_combine_by():
    # 자식 데이터를 가져오는 함수 호출
    child = get_child_course_data()

    # 결과를 저장할 리스트
    combine_by_list = []

    # child course 테이블 순회
    for _, row in child.iterrows():
        father_code = row['FatherCode']
        child_session = row['Session']

        try:
            child_session_split = child_session.split('/')
            child_session_suffix = child_session_split[1] if len(child_session_split) > 1 else child_session_split[0]

            father_courses = FatherCourseOffer.objects.filter(CourseCode=father_code)

            for father_course in father_courses:
                if child_session_suffix in father_course.Session:
                    child_courses = ChildCourseOffer.objects.filter(FatherCode=father_course.CourseCode)

                    combine_by_value = ", ".join(child_courses.values_list('CourseCode', flat=True))
                    combine_by_list.append(combine_by_value)
                else:
                    combine_by_list.append('')
        except FatherCourseOffer.DoesNotExist:
            combine_by_list.append('')

    return combine_by_list


def run():
    df = get_father_course_data()
    rooms_df = get_resource_room_data()

    course_df = split_min_per_session(df)
    # 요일 리스트
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

    # 시간대 리스트
    times = list(range(8, 22))

    # 여러 개의 시간표 생성
    results = generate_timetable(course_df, rooms_df, days, times)

    # 사용되지 않은 강의실 개수가 가장 적은 타임테이블 선택
    best_timetable = min(results, key=lambda x: len(x[1]))

    # 최종 선택된 시간표 출력
    final_timetable, unused_rooms, unassigned_courses = best_timetable
    print("✅ 최종 선택된 시간표:")
    print(final_timetable)
    print(f"🔹 최종 - 사용되지 않은 강의실 개수: {len(unused_rooms)}")
    print(f"🔸 최종 - 배정되지 않은 강의 수: {len(unassigned_courses)}")
    print(final_timetable.columns)

    combine_by_list = make_combine_by()
    final_timetable['CombineBy'] = combine_by_list

    for _, row in final_timetable.iterrows():
        add_assign_row(row)


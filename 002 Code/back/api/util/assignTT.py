import random
import pandas as pd
import math
from django.db.models import Sum
from api.models import FatherCourseOffer, ChildCourseOffer, ResourceRoom


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


# 초기 인구 생성 함수
def initialize_population(size, df, df2, days, times):
    population = []

    for _ in range(size):
        timetable = []
        lecturer_schedule = {lecturer: {day: [] for day in days} for lecturer in df['Lecturer'].unique()}  # 교수님 스케줄 관리

        for _, lecture in df.iterrows():
            total_minutes = lecture['MinPerSession']  # 고정된 수업 시간 (단위: 분)
            total_students = lecture['Capacity']
            lecturer = lecture['Lecturer']

            # 강의실 선택
            room = df2.sample(1).iloc[0]
            day = random.choice(days)

            # 가능한 시간대 필터링
            available_times = [
                t for t in times
                if all(abs(t - scheduled_time) >= 1 for scheduled_time in lecturer_schedule[lecturer][day])
                   and t + math.ceil(total_minutes / 60) <= 22  # 종료 시간이 22시를 넘지 않도록 조건 추가
                   and lecture['CourseCode'] not in [entry['coursecode'] for entry in timetable if entry['day'] == day]
            ]

            if not available_times:
                print(f"Warning: No available times for lecturer {lecturer} on {day}. Assigning default time.")
                available_times = times

            time = random.choice(available_times)
            allocated_students = min(total_students, room['Capacity'])

            timetable.append({
                'facultyCode': lecture['FacultyCode'],
                'coursecode': lecture['CourseCode'],
                'session': lecture['Session'],
                'students': allocated_students,
                'MinPerSession': total_minutes,
                'room': room['ResourceCode'],
                'room_capacity': room['Capacity'],
                'day': day,
                'time': time,
                'Lecturer': lecturer,
                'lecture': room['Lecture'],
                'lab': room['Lab'],
                'tutorial': room['Tutorial'],
                'coursetype': lecture['CourseType']
            })

            lecturer_schedule[lecturer][day].append(time)

        population.append(pd.DataFrame(timetable))
    return population


# 적합도 함수
def fitness_function(timetable):
    score = 0
    penalty = 0

    # 강의실 수용 인원 확인
    for _, row in timetable.iterrows():
        if row['students'] > row['room_capacity']:
            penalty += 10

    # 시간대 중복 확인
    for day in timetable['day'].unique():
        for time in timetable[timetable['day'] == day]['time'].unique():
            rooms_at_time = timetable[(timetable['day'] == day) & (timetable['time'] == time)]['room']
            if len(rooms_at_time) > len(rooms_at_time.unique()):
                penalty += 20

    # 교수님 연속 강의 확인
    for lecturer in timetable['Lecturer'].unique():
        lecturer_schedule = timetable[timetable['Lecturer'] == lecturer].sort_values(by=['day', 'time'])
        for i in range(len(lecturer_schedule) - 1):
            current = lecturer_schedule.iloc[i]
            next_lecture = lecturer_schedule.iloc[i + 1]
            if current['day'] == next_lecture['day'] and abs(current['time'] - next_lecture['time']) < 1:
                penalty += 10

    # 강의 유형 확인
    for _, row in timetable.iterrows():
        if row['coursetype'] == 'Le' and row['lecture'] != 'Y':
            penalty += 30
        if row['coursetype'] == 'La' and row['lab'] != 'Y':
            penalty += 30
        if row['coursetype'] == 'Tu' and row['tutorial'] != 'Y':
            penalty += 30

    # 종료 시간이 22시를 초과하면 페널티 추가
    for _, row in timetable.iterrows():
        if row['time'] + math.ceil(row['MinPerSession'] / 60) > 22:
            penalty += 50

    return score - penalty


# 교차 연산
def crossover(parent1, parent2, days, times):
    point = random.randint(0, len(parent1) - 1)
    child = pd.concat([parent1.iloc[:point], parent2.iloc[point:]]).reset_index(drop=True)

    for index, row in child.iterrows():
        same_time_lectures = child[(child['day'] == row['day']) & (child['time'] == row['time'])]
        if len(same_time_lectures) > 1:
            available_times = [t for t in times if t != row['time']]
            child.at[index, 'time'] = random.choice(available_times)

        same_room_lectures = child[
            (child['day'] == row['day']) & (child['time'] == row['time']) & (child['room'] == row['room'])]
        if len(same_room_lectures) > 1:
            new_room = parent1.sample(1).iloc[0]['room'] if random.random() > 0.5 else parent2.sample(1).iloc[0]['room']
            child.at[index, 'room'] = new_room

    return child


# 변이 연산
def mutate(timetable, times, mutation_rate=0.1):
    for index, row in timetable.iterrows():
        if random.random() < mutation_rate:
            new_day = random.choice(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])
            available_times = [t for t in times if t + math.ceil(row['MinPerSession'] / 60) <= 22]
            if available_times:
                new_time = random.choice(available_times)
                timetable.at[index, 'day'] = new_day
                timetable.at[index, 'time'] = new_time
    return timetable


# 유전 알고리즘 실행
def genetic_algorithm(df, df2, days, times, population_size, generations, mutation_rate=0.1):
    population = initialize_population(population_size, df, df2, days, times)
    for generation in range(generations):
        population = sorted(population, key=fitness_function, reverse=True)
        new_population = population[:10]
        while len(new_population) < population_size:
            parent1, parent2 = random.sample(population[:50], 2)
            child = crossover(parent1, parent2, days, times)
            if random.random() < mutation_rate:
                child = mutate(child, times, mutation_rate)
            new_population.append(child)
        population = new_population
        print(f"Generation {generation + 1}: Best fitness = {fitness_function(population[0])}")
    return max(population, key=fitness_function)


def timetable_to_table(timetable):
    # 요일 및 시간대 초기화
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    times = [f"{hour}:00" for hour in range(8, 22)]

    # 빈 데이터프레임 생성
    timetable_df = pd.DataFrame('', index=times, columns=days)

    # 데이터 채우기
    for _, row in timetable.iterrows():
        day = row['day']
        time = f"{row['time']}:00"
        course_info = f"{row['coursecode']} ({row['room']})"
        if timetable_df.loc[time, day]:  # 이미 값이 있으면 여러 강의 표시
            timetable_df.loc[time, day] += f", {course_info}"
        else:
            timetable_df.loc[time, day] = course_info

    return timetable_df


def get_father_course_data():
    father_courses = FatherCourseOffer.objects.values(
        "CourseCode", "FacultyCode", "Session", "Capacity",
        "MinPerSession", "Lecturer", "CourseType"
    )

    child_capacity = ChildCourseOffer.objects.values("FatherCode").annotate(
        total_capacity=Sum("Capacity")
    )

    child_capacity_dict = {entry["FatherCode"]: entry["total_capacity"] for entry in child_capacity}

    df = pd.DataFrame(list(father_courses))

    df["Capacity"] += df["CourseCode"].map(child_capacity_dict).fillna(0).astype(int)

    return df


def get_father_course_data2():
    # FatherCourseOffer에서 부모 데이터 가져오기
    father_courses = FatherCourseOffer.objects.values(
        "CourseCode", "FacultyCode", "Session", "Capacity",
        "MinPerSession", "Lecturer", "CourseType"
    )

    # ChildCourseOffer에서 자식 데이터 가져오기, 총 Capacity 합산
    child_capacity = ChildCourseOffer.objects.values("FatherCode", "Session").annotate(
        total_capacity=Sum("Capacity")
    )

    print(len(child_capacity))

    # child_capacity를 딕셔너리로 변환
    child_capacity_dict = {}
    for entry in child_capacity:
        father_code = entry["FatherCode"]
        session = entry["Session"].split("/")[1] if "/" in entry["Session"] else entry["Session"]
        print(session)
        if father_code not in child_capacity_dict:
            child_capacity_dict[father_code] = {}

        child_capacity_dict[father_code][session] = entry["total_capacity"]

    # 데이터프레임으로 변환
    df = pd.DataFrame(list(father_courses))

    def add_child_capacity(row):
        father_code = row["CourseCode"]
        parent_session = row["Session"]

        # 자식의 Session 값이 부모의 Session에 포함되는지 확인
        child_capacity_for_father = child_capacity_dict.get(father_code, {})
        for child_session, capacity in child_capacity_for_father.items():
            if child_session in parent_session:
                row["Capacity"] += capacity

        return row

    # 각 부모 행에 대해 자식 Capacity 합산
    df = df.apply(add_child_capacity, axis=1)

    return df


def get_resource_room_data():
    resource_rooms = ResourceRoom.objects.values(
        "id", "ResourceCode", "Description", "Capacity",
        "Lecture", "Tutorial", "Lab", "ETC"
    )

    df = pd.DataFrame(list(resource_rooms))

    return df


def get_child_course_data():
    child = ChildCourseOffer.objects.values(
        "id", "FatherCode", "CourseCode", "Capacity", "Session"
    )

    df = pd.DataFrame(list(child))

    return df


def apply_assign_table():
    merged_course_df = get_father_course_data()
    resource_room_df = get_resource_room_data()

    df = split_min_per_session(merged_course_df)
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    times = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]

    # 유전 알고리즘 실행
    best_timetable = genetic_algorithm(df, resource_room_df, days, times, population_size=10, generations=50,
                                       mutation_rate=0.1)

    return best_timetable


def get_time_table():
    df = apply_assign_table()

    timetable = df[
        ['facultyCode', 'coursecode', 'session', 'room', 'students', 'room_capacity', 'day', 'time', 'Lecturer']]

    child = get_child_course_data()

    # 결과를 저장할 리스트
    combine_by_list = []

    for _, row in child.iterrows():
        father_code = row['FatherCode']
        child_session = row['Session']

        child_session_split = child_session.split('/')
        session = child_session_split[1] if len(child_session_split) > 1 else child_session_split[0]

        father_courses = FatherCourseOffer.objects.filter(CourseCode=father_code)

        matching_father_courses = []

        for father_course in father_courses:
            if session in father_course.Session:
                matching_father_courses.append(father_course.CourseCode)

            combine_by_value = ", ".join(matching_father_courses) if matching_father_courses else ''
            combine_by_list.append(combine_by_value)

        if len(combine_by_list) > 0:
            timetable['CombineBy'] = combine_by_list

    print(timetable)

    return timetable
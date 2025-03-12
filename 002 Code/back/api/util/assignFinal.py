import random
import pandas as pd
from api.util.assignTT import get_father_course_data, get_resource_room_data, get_child_course_data
from api.util.rows import add_assign_row, add_ng_resource_row, add_ng_course_row


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
    unassigned_lectures = []  # 배정되지 않은 강의 저장

    for _ in range(size):
        timetable = []
        professor_schedule = {}  # 교수별 배정된 시간 저장 (교수 ID -> (요일, 시작 시간, 종료 시간) 리스트)
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
            available_slots = []
            for d in days:
                for t in times:
                    end_t = t + session_duration
                    # 교수의 기존 강의와 시간 겹침 여부 확인
                    professor_conflict = any(
                        scheduled_day == d and not (end_t <= scheduled_start or t >= scheduled_end)
                        for scheduled_day, scheduled_start, scheduled_end in professor_schedule[professor]
                    )

                    # Split_ID 중복 확인
                    split_conflict = split_id and any(
                        scheduled_day == d and not (end_t <= scheduled_start or t >= scheduled_end)
                        for scheduled_day, scheduled_start, scheduled_end in split_schedule[split_id]
                    )

                    # 22시 초과 방지
                    if not professor_conflict and not split_conflict and end_t <= 22:
                        available_slots.append((d, t, end_t))

            if not available_slots:
                print(f"❌ No available slots for {lecture['CourseCode']} - Skipping")
                unassigned_lectures.append(lecture['CourseCode'])  # 배정 실패한 강의 저장
                continue

            new_day, new_start_time, new_end_time = random.choice(available_slots)  # 충돌 없는 시간 선택

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
                'start_time': new_start_time,
                'end_time': new_end_time,
                'MinPerSession': session_duration,
                'CombineBy': '',
            })

            # 교수 및 Split_ID 스케줄 업데이트
            professor_schedule[professor].append((new_day, new_start_time, new_end_time))
            if split_id:
                split_schedule[split_id].append((new_day, new_start_time, new_end_time))

        timetable = pd.DataFrame(timetable)
        population.append(timetable)

    # 배정되지 않은 강의 출력
    print("\n📌 배정되지 않은 강의 목록:")
    if unassigned_lectures:
        print(f"총 {len(unassigned_lectures)}개 강의 배정 실패")
        print(unassigned_lectures)
    else:
        print("모든 강의가 성공적으로 배정됨 ✅")

    return population


def assign_rooms(timetable_df, rooms_df):
    updated_timetable = []
    unassigned_lectures = []
    room_schedule = {}  # {room_name: [(day, start_time, end_time), ...]}
    room_usage_count = {room: 0 for room in rooms_df['ResourceCode']}  # 강의실 사용 횟수

    def get_available_rooms(capacity_needed, course_type=None):
        """ 특정 강의 유형 또는 전체 강의실 중 조건에 맞는 강의실을 반환 """
        if course_type:
            if course_type == 'Le':
                available_rooms = rooms_df[(rooms_df['Capacity'] >= capacity_needed) & (rooms_df['Lecture'] == 'Y')]
            elif course_type == 'La':
                available_rooms = rooms_df[(rooms_df['Capacity'] >= capacity_needed) & (rooms_df['Lab'] == 'Y')]
            elif course_type == 'Tu':
                available_rooms = rooms_df[(rooms_df['Capacity'] >= capacity_needed) & (rooms_df['Tutorial'] == 'Y')]
            elif course_type == 'ETC':
                available_rooms = rooms_df[rooms_df['Capacity'] >= capacity_needed]
            else:
                return pd.DataFrame()
        else:
            available_rooms = rooms_df[rooms_df['Capacity'] >= capacity_needed]

        available_rooms = available_rooms.copy()
        available_rooms["excess_capacity"] = available_rooms["Capacity"] - capacity_needed
        available_rooms = available_rooms.sort_values(by=["excess_capacity", "Capacity"], ascending=[True, True])

        return available_rooms.copy()

    def assign_lecture(lecture, available_rooms):
        """ 시간 충돌을 피해서 강의실 배정 (최소 사용 강의실 원칙) """
        non_conflicting_rooms = []
        day, start_time, end_time = lecture['day'], lecture['start_time'], lecture['end_time']

        for _, room in available_rooms.iterrows():
            room_name = room['ResourceCode']
            if room_name not in room_schedule:
                room_schedule[room_name] = []

            conflict = any(
                scheduled_day == day and not (end_time <= scheduled_start or start_time >= scheduled_end)
                for scheduled_day, scheduled_start, scheduled_end in room_schedule[room_name]
            )
            if not conflict:
                non_conflicting_rooms.append(room)

        if non_conflicting_rooms:
            non_conflicting_rooms = sorted(non_conflicting_rooms, key=lambda x: room_usage_count[x['ResourceCode']])
            selected_room = non_conflicting_rooms[0]
            room_name = selected_room['ResourceCode']
            room_schedule[room_name].append((day, start_time, end_time))
            room_usage_count[room_name] += 1
            return room_name, selected_room['Capacity']
        return None, None

    for _, lecture in timetable_df.iterrows():
        capacity_needed = lecture['capacity']
        course_type = lecture['CourseType']

        available_rooms = get_available_rooms(capacity_needed, course_type)
        room_name, room_capacity = assign_lecture(lecture, available_rooms)

        if room_name:
            updated_timetable.append({**lecture, 'room': room_name, 'room_capacity': room_capacity})
        else:
            unassigned_lectures.append(lecture)

    for lecture in unassigned_lectures:
        available_rooms = get_available_rooms(lecture['capacity'])
        room_name, room_capacity = assign_lecture(lecture, available_rooms)

        if room_name:
            updated_timetable.append({**lecture, 'room': room_name, 'room_capacity': room_capacity})
        else:
            print(f"⚠️ 모든 강의실을 확인했지만 배정 불가 → 랜덤 배정: {lecture['coursecode']}")
            remaining_rooms = rooms_df[~rooms_df['ResourceCode'].isin(room_schedule.keys())]
            if not remaining_rooms.empty:
                random_room = remaining_rooms.iloc[0]['ResourceCode']
            else:
                random_room = min(room_usage_count, key=room_usage_count.get)
            updated_timetable.append({
                **lecture,
                'room': random_room,
                'room_capacity': rooms_df.loc[rooms_df['ResourceCode'] == random_room, 'Capacity'].values[0]
            })

    return pd.DataFrame(updated_timetable)


def generate_timetable(course_df, rooms_df, days, times):
    population = initialize_population(20, course_df, days, times)
    print("✅ Population initialized successfully!")

    assigned_population = [assign_rooms(timetable, rooms_df) for timetable in population]
    print("✅ Rooms assigned successfully!")

    results = []
    for timetable in assigned_population:
        # all_rooms = set(rooms_df['ResourceCode'])
        assigned_rooms = set(timetable['room'].dropna())
        # unused_rooms = all_rooms - assigned_rooms

        unused_rooms = rooms_df[~rooms_df['ResourceCode'].isin(assigned_rooms)].reset_index(drop=True)
        unassigned_courses = timetable[timetable['room'].isna()]

        results.append((timetable, unused_rooms, unassigned_courses))

    print("✅ Timetable generation completed successfully!")
    return results


def check_constraints(final_timetable):
    """
    시간표에서 강의실 중복, 교수 중복, 강의실 수용 인원 초과, 연속 강의 시간 충돌,
    점심시간 및 저녁시간 강의 여부를 체크하는 함수
    """
    constraint_violations = []

    # 강의실별 중복 체크
    room_conflicts = {}
    for idx, row in final_timetable.iterrows():
        room, day, start_time, end_time = row['room'], row['day'], row['start_time'], row['end_time']

        if room:  # 강의실이 배정된 경우만 체크
            if room not in room_conflicts:
                room_conflicts[room] = []
            for scheduled_day, scheduled_start, scheduled_end in room_conflicts[room]:
                if scheduled_day == day and not (end_time <= scheduled_start or start_time >= scheduled_end):
                    constraint_violations.append(
                        f"🚨 Room Conflict: {room} is double-booked on {day} from {start_time} to {end_time}"
                    )
            room_conflicts[room].append((day, start_time, end_time))

    # 교수별 중복 체크
    professor_conflicts = {}
    for idx, row in final_timetable.iterrows():
        professor, day, start_time, end_time = row['professor'], row['day'], row['start_time'], row['end_time']

        if professor not in professor_conflicts:
            professor_conflicts[professor] = []
        for scheduled_day, scheduled_start, scheduled_end in professor_conflicts[professor]:
            if scheduled_day == day and not (end_time <= scheduled_start or start_time >= scheduled_end):
                constraint_violations.append(
                    f"🚨 Professor Conflict: {professor} is scheduled for multiple lectures on {day} from {start_time} to {end_time}"
                )
        professor_conflicts[professor].append((day, start_time, end_time))

    # 강의실 수용 인원 초과 체크
    for idx, row in final_timetable.iterrows():
        assigned_capacity, required_capacity = row['room_capacity'], row['capacity']

        if required_capacity > assigned_capacity:
            constraint_violations.append(
                f"⚠️ Capacity Overflow: {row['room']} cannot accommodate {required_capacity} students (Max: {assigned_capacity})"
            )

    # 연속 강의 시간 충돌 (split_id)
    split_conflicts = {}
    for idx, row in final_timetable.iterrows():
        split_id, day, start_time, end_time = row.get('split_id'), row['day'], row['start_time'], row['end_time']

        if split_id and not pd.isna(split_id):
            if split_id not in split_conflicts:
                split_conflicts[split_id] = []
            for scheduled_day, scheduled_start, scheduled_end in split_conflicts[split_id]:
                if scheduled_day == day and not (end_time <= scheduled_start or start_time >= scheduled_end):
                    constraint_violations.append(
                        f"⚠️ Split Conflict: Course {split_id} has overlapping lectures on {day} from {start_time} to {end_time}"
                    )
            split_conflicts[split_id].append((day, start_time, end_time))

    return constraint_violations


# 최적의 시간표 선택 기준 (제약 위반 개수 + 사용되지 않은 강의실 개수)
def evaluate_timetable(timetable_result):
    final_timetable, unused_rooms, unassigned_courses = timetable_result
    violations = check_constraints(final_timetable)
    return len(violations) + len(unused_rooms)  # 평가 점수: 제약 위반 개수 + 사용되지 않은 강의실 개수


def assign_table():
    # 요일 리스트
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

    # 시간대 리스트
    times = list(range(8, 22))

    df = get_father_course_data()
    rooms_df = get_resource_room_data()

    course_df = split_min_per_session(df)

    results = generate_timetable(course_df, rooms_df, days, times)

    # 최적의 시간표 선택 (제약 위반이 적고, 사용되지 않은 강의실이 적은 시간표)
    best_timetable = min(results, key=evaluate_timetable)

    # 최종 선택된 시간표 출력
    final_timetable, unused_rooms, unassigned_courses = best_timetable

    print("✅ 최종 선택된 시간표:")
    print(final_timetable)
    for _, row in final_timetable.iterrows():
        add_assign_row(row)

    print(f"🔹 최종 - 사용되지 않은 강의실 개수: {len(unused_rooms)}")
    for _, row in unused_rooms.iterrows():
        add_ng_resource_row(row)

    print(f"🔸 최종 - 배정되지 않은 강의 수: {len(unassigned_courses)}")
    for _, row in unassigned_courses.iterrows():
        add_ng_course_row(row)

    # 제약 위반 사항 출력
    violations = check_constraints(final_timetable)
    print(f"⚠️ 최종 - 제약 위반 개수: {len(violations)}")
    if violations:
        print("🚨 제약 위반 사항:")
        for v in violations:
            print(v)

import numpy as np
import pandas as pd

from api.process.create_cost_matrix import create_cost_matrix
from api.process.expand_room_slots import expand_room_slots
from scipy.optimize import linear_sum_assignment


def assign_classes(df_final, offer):
    df_final_expanded = expand_room_slots(df_final)
    cost_matrix = create_cost_matrix(df_final_expanded, offer)

    num_offers, num_rooms = cost_matrix.shape
    max_size = max(num_offers, num_rooms)

    if num_offers < max_size:
        cost_matrix = np.vstack([cost_matrix, np.full((max_size - num_offers, max_size), 1e6)])
    if num_rooms < max_size:
        cost_matrix = np.hstack([cost_matrix, np.full((max_size, max_size - num_rooms), 1e6)])

    row_ind, col_ind = linear_sum_assignment(cost_matrix)

    assignments = []
    professor_time_map = {}  # 🔹 교수님 시간 중복 체크

    for r, c in zip(row_ind, col_ind):
        if r < len(offer) and c < len(df_final_expanded) and cost_matrix[r, c] != 1e6:
            assigned_day = df_final_expanded.iloc[c]['Assigned Day']
            assigned_time = df_final_expanded.iloc[c]['Assigned Time Slot']
            professor = offer.iloc[r]['Lecturer']

            # 🔹 같은 시간에 같은 교수님이 이미 배정된 경우 무조건 제외
            if (assigned_day, assigned_time) in professor_time_map and professor in professor_time_map[(assigned_day, assigned_time)]:
                continue  # 🚨 이 배정은 무효! 스킵!

            # 🔹 교수님 배정 확정 (시간대 저장)
            if (assigned_day, assigned_time) not in professor_time_map:
                professor_time_map[(assigned_day, assigned_time)] = set()
            professor_time_map[(assigned_day, assigned_time)].add(professor)

            assignments.append({
                'Group': offer.iloc[r]['Course Code'],
                'Category': offer.iloc[r]['Category'],
                'Lecturer': professor,
                'Assigned Room': df_final_expanded.iloc[c]['Resource Code'],
                'Room Type': df_final_expanded.iloc[c]['Type'],
                'Group Capacity': offer.iloc[r]['Capacity'],
                'Room Capacity': df_final_expanded.iloc[c]['Capacity'],
                'Assigned Day': assigned_day,
                'Assigned Time Slot': assigned_time,
                'Lecture': df_final_expanded.iloc[c]['Lecture'],
                'Tutorial': df_final_expanded.iloc[c]['Tutorial'],
                'Lab': df_final_expanded.iloc[c]['Lab'],
                'Duration (min)': offer.iloc[r]['Min Per Session']
            })

    return pd.DataFrame(assignments)
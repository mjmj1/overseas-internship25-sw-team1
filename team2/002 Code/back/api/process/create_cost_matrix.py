import numpy as np


def create_cost_matrix(df_final, offer):
    num_offers = len(offer)
    num_rooms = len(df_final)
    max_size = max(num_offers, num_rooms)
    cost_matrix = np.full((max_size, max_size), 1e6)

    df_final['Capacity'] = df_final['Capacity'].astype(int)
    offer['Capacity'] = offer['Capacity'].astype(int)

    # 🔹 교수님이 특정 시간에 중복되지 않도록 하기 위한 매핑
    professor_time_map = {}

    for i, offer_row in offer.iterrows():
        for j, room_row in df_final.iterrows():
            assigned_time = (room_row['Assigned Day'], room_row['Assigned Time Slot'])
            professor = offer_row['Lecturer']

            if (offer_row['Category'] == room_row['Type'] or
                (offer_row['Category'] in ['lecture', 'tutorial'] and room_row['Type'] in ['general', 'lecture']) or
                (offer_row['Category'] == 'lecture' and room_row['Type'] == 'tutorial' and room_row['Lecture'] == 'Y')):

                if room_row['Capacity'] >= offer_row['Capacity']:
                    # 🔹 같은 시간대에 이미 배정된 교수님이 있는 경우 패널티를 줌
                    if assigned_time in professor_time_map and professor in professor_time_map[assigned_time]:
                        cost_matrix[i, j] = 1e6  # 불가능한 배정 (큰 값)
                    else:
                        cost_matrix[i, j] = room_row['Capacity'] - offer_row['Capacity']

    return cost_matrix

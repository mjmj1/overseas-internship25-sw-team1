import pandas as pd

def preprocess_offers(offer, max_room_capacity):
    expanded_offers = []
    for _, row in offer.iterrows():
        remaining_students = row['Capacity']
        total_duration = row['Min Per Session']
        session_count = 1

        while remaining_students > 0:
            assigned_capacity = min(max_room_capacity, remaining_students)
            remaining_students -= assigned_capacity

            remaining_duration = total_duration
            sub_session = 1

            while remaining_duration > 0:
                session_duration = min(180, remaining_duration)
                remaining_duration -= session_duration

                expanded_offers.append({
                    'Course Code': f"{row['CourseCode']}_S{session_count}_D{sub_session}",
                    'Capacity': assigned_capacity,
                    'Min Per Session': session_duration,
                    'Category': row['Category'],
                    'Lecturer': row['Lecturer']
                })
                sub_session += 1

            session_count += 1

    return pd.DataFrame(expanded_offers)
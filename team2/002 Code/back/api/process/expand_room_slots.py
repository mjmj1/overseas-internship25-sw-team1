def expand_room_slots(df_final):
    time_slots = ['8-11', '13-16', '18-21']
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']

    expanded_rooms = []
    for _, row in df_final.iterrows():
        for day in days:
            for time in time_slots:
                expanded_rooms.append({
                    'Resource Code': row['Resource Code'],
                    'Type': row['Type'],
                    'Capacity': row['Capacity'],
                    'Assigned Day': day,
                    'Assigned Time Slot': time,
                    'Lecture': row.get('Lecture', 'N'),
                    'Tutorial': row.get('Tutorial', 'N'),
                    'Lab': row.get('Lab', 'N')
                })

    import pandas as pd
    return pd.DataFrame(expanded_rooms)
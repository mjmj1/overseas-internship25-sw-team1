import pandas as pd


def process_resource_room(filepath):
    """
    Processes the resource room Excel file and returns a cleaned and categorized DataFrame.

    Parameters:
        filepath (str): The path to the Excel file (e.g., '/content/CSD - Resource Room.xlsx').

    Returns:
        pd.DataFrame: The processed DataFrame with an added 'Type' column.
    """
    df = pd.read_excel(filepath)

    # Remove unwanted columns
    df = df.drop(labels='Campus', axis=1)
    df = df.drop(labels='Workshop', axis=1)

    # Exclude rows containing 'IMus'
    df = df[~df.apply(lambda row: row.astype(str).str.contains('IMus', case=False, na=False).any(), axis=1)]

    # Exclude rows where Lecture, Tutorial, Lab are all 'N'
    df = df[~(df[['Lecture', 'Tutorial', 'Lab']].eq('N').all(axis=1))]

    # Fill NA values with 'N' and replace 'N' in Capacity with '20'
    df = df.fillna('N')
    df['Capacity'] = df['Capacity'].replace('N', '20')

    # Drop rows with Capacity equal to 0
    df = df.drop(df[df['Capacity'] == 0].index)

    # Categorize as General where Lecture, Tutorial, Lab are all 'Y'
    conditions = [['Y', 'Y', 'Y']]
    columns_to_check = ['Lecture', 'Tutorial', 'Lab']
    General = df[df[columns_to_check].apply(tuple, axis=1).isin(map(tuple, conditions))]

    # Exclude specific conditions to form etc_Room
    conditions_to_exclude = [['Y', 'Y', 'N'], ['N', 'Y', 'Y']]
    etc_Room = df[~df[columns_to_check].apply(tuple, axis=1).isin(map(tuple, conditions))]

    Kitchen = etc_Room[etc_Room.apply(lambda row: row.astype(str).str.contains('Kitchen', regex=False).any(), axis=1)]
    Design = etc_Room[etc_Room['Description'].str.contains('DESIGN', case=False, na=False)]

    df_combined = pd.concat([Kitchen, Design])
    LL = etc_Room[~etc_Room.apply(tuple, axis=1).isin(df_combined.apply(tuple, axis=1))]

    # Categorize Lab rooms: where [Lecture, Tutorial, Lab] == ['N', 'N', 'Y']
    lab_condition = [['N', 'N', 'Y']]
    Lab = LL[LL[columns_to_check].apply(tuple, axis=1).isin(map(tuple, lab_condition))]

    # Categorize Lecture rooms: where [Lecture, Tutorial, Lab] == ['Y', 'N', 'N']
    lecture_condition = [['Y', 'N', 'N']]
    Lecture = LL[LL[columns_to_check].apply(tuple, axis=1).isin(map(tuple, lecture_condition))]

    df_combined = pd.concat([Lab, Lecture])
    ETC = LL[~LL.apply(tuple, 1).isin(df_combined.apply(tuple, 1))]

    # Assign types
    General['Type'] = 'General'
    Lab['Type'] = 'Lab'
    Kitchen['Type'] = 'Kitchen'
    Design['Type'] = 'Art'
    Lecture['Type'] = 'Lecture'
    ETC['Type'] = 'Etc'

    # Combine all categorized DataFrames
    df_final = pd.concat([General, ETC, Kitchen, Design, Lab, Lecture], ignore_index=True)
    df_final = df_final.drop_duplicates(keep='first')
    df_final.loc[df_final.astype(str).apply(lambda row: row.str.contains('PBL', case=False, na=False).any(),
                                            axis=1), 'Type'] = 'PBL'

    return df_final

# import pandas as pd
#
#
# def process_resource_room(filepath):
#     df = pd.read_excel(filepath)  # 엑셀 파일을 읽어옵니다.
#     Resource_Room = pd.DataFrame(df)
#
#     # 불필요한 열 제거
#     Resource_Room = Resource_Room.drop(labels='Campus', axis=1)
#     Resource_Room = Resource_Room.drop(labels='Workshop', axis=1)
#
#     # 'IMus' 포함된 행 제거
#     Resource_Room = Resource_Room[
#         ~Resource_Room.apply(lambda row: row.astype(str).str.contains('IMus', case=False, na=False).any(), axis=1)]
#
#     # 'Lecture', 'Tutorial', 'Lab'가 모두 'N'인 행 제외
#     Resource_Room = Resource_Room[~(Resource_Room[['Lecture', 'Tutorial', 'Lab']].eq('N').all(axis=1))]
#
#     # NA 값 'N'으로 채우고, 'N'인 Capacity는 '20'으로 설정
#     Resource_Room = Resource_Room.fillna('N')
#     Resource_Room['Capacity'] = Resource_Room['Capacity'].replace('N', '20')
#
#     # Capacity가 0인 행 제거
#     Resource_Room = Resource_Room.drop(Resource_Room[Resource_Room['Capacity'] == 0].index)
#
#     return Resource_Room
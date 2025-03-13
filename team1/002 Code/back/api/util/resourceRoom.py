import os
import pandas as pd
from django.conf import settings
from api.models import ResourceRoom

RESOURCEROOMPATH = 'CSD - Resource Room.xlsx'


def make_resource_table():
    file_path = os.path.join(settings.BASE_DIR, 'datas', RESOURCEROOMPATH)
    if not os.path.exists(file_path):
        print("파일이 존재하지 않습니다.")
        return

    df = pd.read_excel(file_path)

    df = add_room_tag(df)

    df.fillna({
        'Lecture': 'N',
        'Tutorial': 'N',
        'Lab': 'N',
        'ETC': 'N',
    }, inplace=True)

    data_list = []

    for _, row in df.iterrows():
        data = ResourceRoom(
            ResourceCode=row['Resource Code'],
            Description=row['Description'],
            Capacity=row['Capacity'],
            Lecture=row['Lecture'],
            Tutorial=row['Tutorial'],
            Lab=row['Lab'],
            ETC=row['ETC'],
        )

        data_list.append(data)

    ResourceRoom.objects.bulk_create(data_list)

    print("데이터베이스에 데이터 저장 완료!")


def add_room_tag(df):
    keywords = ['imus', 'kitchen', 'pbl']
    df['ETC'] = df['Resource Code'].apply(
        lambda x: 'Y' if any(keyword in str(x).lower() for keyword in keywords) else 'N')
    return df

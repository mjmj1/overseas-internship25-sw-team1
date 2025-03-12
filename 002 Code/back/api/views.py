from django.http import JsonResponse
from django.shortcuts import render

from api.process.generate_assigned_schedule import generate_assigned_schedule
from api.process.preprocess_offer import preprocess_offer
from api.process.process_resource_room import process_resource_room
from config.settings import BASE_DIR
from api.models import AssignTable
from django.db import transaction


# Create your views here.
def process_data(request):
    # 엑셀 파일 경로
    resource_room_filepath = f'{BASE_DIR}/data/Resource_Room.xlsx'
    offer_filepath = f'{BASE_DIR}/data/Course_Offer.xlsx'

    # 데이터 불러오기 및 전처리
    processed_resource_room = process_resource_room(resource_room_filepath)
    processed_offer = preprocess_offer(offer_filepath)

    # 강의실 배정 알고리즘 수행
    assigned_schedule = generate_assigned_schedule(processed_resource_room, processed_offer)

    with transaction.atomic():  # 🔹 트랜잭션 사용 (오류 발생 시 롤백)
        courses = [
            AssignTable(
                group=row["Group"],
                category=row["Category"],
                lecturer=row["Lecturer"],
                assigned_room=row["Assigned Room"],
                room_type=row["Room Type"],
                group_capacity=row["Group Capacity"],
                room_capacity=row["Room Capacity"],
                assigned_day=row["Assigned Day"],
                assigned_time_slot=row["Assigned Time Slot"],
                lecture=row["Lecture"],
                tutorial=row["Tutorial"],
                lab=row["Lab"],
                duration=row["Duration (min)"]
            )
            for _, row in assigned_schedule.iterrows()
        ]
        AssignTable.objects.bulk_create(courses)

    # 결과를 JSON 형식으로 반환
    return JsonResponse({'assigned_schedule': assigned_schedule.to_dict(orient='records')})

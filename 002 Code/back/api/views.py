from django.shortcuts import render

from django.http import HttpResponse, JsonResponse

from api.util.assignFinal import assign_table
from api.util.resourceRoom import make_resource_table
from api.util.courseOffer import make_course_tables

from api.models import AssignTable, FatherCourseOffer

def home(request):
    # make_resource_table()
    # make_course_tables()
    # assign_table()
    return JsonResponse({"message": "성공적으로 DB에 저장되었습니다."})

def make(request):
    make_resource_table()
    make_course_tables()
    assign_table()
    return JsonResponse({"message": "성공적으로 DB에 저장되었습니다."})

def make_resource(request):
    if request.method == 'GET':
        make_resource_table()
        return JsonResponse({"message": "성공적으로 DB에 저장되었습니다."})
    return JsonResponse({"error": "GET 요청만 허용됩니다."}, status=400)


def make_course(request):
    if request.method == 'GET':
        make_course_tables()
        return JsonResponse({"message": "성공적으로 DB에 저장되었습니다."})
    return JsonResponse({"error": "GET 요청만 허용됩니다."}, status=400)


def make_assign_table(request):
    code = request.GET.get('facultyCode', None)

    assign_table()

    filtered_data = AssignTable.objects.filter(FacultyCode=code)
    return JsonResponse(list(filtered_data.values()), safe=False)

def get_assign_table(request):
    code = request.GET.get('facultyCode', None)

    if code is None:
        return JsonResponse("")

    filtered_data = AssignTable.objects.filter(FacultyCode=code)
    return JsonResponse(list(filtered_data.values()), safe=False)


def get_father_course_offer(request):
    code = request.GET.get('facultyCode', None)

    if code is None:
        return JsonResponse("")

    filtered_data = FatherCourseOffer.objects.filter(FacultyCode=code)
    return JsonResponse(list(filtered_data.values()), safe=False)
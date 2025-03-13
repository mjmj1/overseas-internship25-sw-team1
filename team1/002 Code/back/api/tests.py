import pandas as pd
from django.test import TestCase
from api.models import FatherCourseOffer, ChildCourseOffer
from api.util.assignTT import get_father_course_data2, get_time_table  # 함수가 있는 모듈을 import
class GetTimeTableTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        """한 번만 실행되는 테스트 데이터 세팅"""
        cls.father1 = FatherCourseOffer.objects.create(
            CourseCode="CS101",
            FacultyCode="ENG1",
            Session="Fall 2024",
            Capacity=100,
            MinPerSession=30,
            Lecturer="Dr. Kim",
            CourseType="Le"
        )

        cls.father2 = FatherCourseOffer.objects.create(
            CourseCode="CS102",
            FacultyCode="ENG2",
            Session="Spring 2025",
            Capacity=80,
            MinPerSession=25,
            Lecturer="Prof. Lee",
            CourseType="Tu"
        )

        ChildCourseOffer.objects.create(FatherCode="CS101", CourseCode="CCS101", Capacity=50, Session="combine to /Fall 2024")
        ChildCourseOffer.objects.create(FatherCode="CS101", CourseCode="CCS102", Capacity=30, Session="combine to /Fall 2025")
        ChildCourseOffer.objects.create(FatherCode="CS102", CourseCode="CCS103", Capacity=20, Session="combine to /Spring 2025")

        # 가상의 데이터프레임 생성 (apply_assign_table 함수가 반환하는 값과 유사하게 구성)
        cls.mock_df = pd.DataFrame({
            'facultyCode': ['ENG'],
            'coursecode': ['CS101'],
            'session': ['2024-01'],
            'room': ['A101'],
            'students': [30],
            'room_capacity': [50],
            'day': ['Monday'],
            'time': ['10:00 AM'],
            'Lecturer': ['Dr. Smith']
        })

    def test_get_time_table(self):
        """get_time_table 함수가 올바른 데이터를 반환하는지 테스트"""
        # 가짜 데이터를 반환하도록 apply_assign_table을 모킹
        with self.subTest("Mocking apply_assign_table"):
            original_function = globals().get("apply_assign_table")
            globals()["apply_assign_table"] = lambda: self.mock_df  # apply_assign_table을 가짜 함수로 대체

        try:
            get_time_table()  # 함수 실행

            # 예상된 결과 확인
            expected_combine_by = "CS101A,CS101B"  # CS101의 child courses
            timetable = apply_assign_table()  # 함수 실행 후 DF 확인

            self.assertIn('CombineBy', timetable.columns, "CombineBy 컬럼이 존재해야 합니다.")
            self.assertEqual(timetable.iloc[0]['CombineBy'], expected_combine_by, "CS101A, CS101B가 포함되어야 함")

        finally:
            if original_function:
                globals()["apply_assign_table"] = original_function  # 원래 함수로 복구


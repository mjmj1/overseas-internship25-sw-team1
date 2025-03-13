from rest_framework import serializers
from api.models import AssignTable, FatherCourseOffer


class FatherCourseOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = FatherCourseOffer
        fields = '__all__'  # 모든 필드를 포함

class AssignTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignTable
        fields = '__all__'  # 모든 필드를 포함
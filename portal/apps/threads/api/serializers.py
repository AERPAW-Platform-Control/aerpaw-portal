from rest_framework import serializers

from portal.apps.threads.models import AerpawThread, ThreadQue

class AerpawThreadSerializer(serializers.ModelSerializer):
    class Meta:
        model = AerpawThread
        fields = '__all__'


class ThreadQueSerializer(serializers.ModelSerializer):
    threads = AerpawThreadSerializer(many=True, read_only=True)
    
    class Meta:
        model = ThreadQue
        fields = ('id', 'is_threading', 'name', 'target', 'threads')
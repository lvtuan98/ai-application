from rest_framework import serializers
from docgen_api.models import SubcriptionRequest

class ReportSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    request_id = serializers.CharField(required=False)
    prompt = serializers.CharField()
    location = serializers.CharField()
    result = serializers.CharField()

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return SubcriptionRequest.objects.create(**validated_data)

    def update(self, instance, validated_data):
        return instance
    
    def _parse_output(self, obj: SubcriptionRequest, data: dict):
        if obj is None or data is None:
            return None
        
        outputs = data.get("content", {})
        model_status = data.get("status", 404)
        return {
            "status": model_status,
            "content": outputs
        }

    def get_data(self, obj: SubcriptionRequest):
        data = obj.result
        return self._parse_output(obj, data)
    
    def get_files(self, obj: SubcriptionRequest):
        return None
from rest_framework import serializers

class CNICVerificationSerializer(serializers.Serializer):
    image = serializers.CharField()  # Base64-encoded image
    extracted_text = serializers.CharField(read_only=True)
    valid = serializers.BooleanField(read_only=True)
    cnic_number = serializers.CharField(read_only=True, allow_null=True)
    error = serializers.CharField(read_only=True, allow_null=True)









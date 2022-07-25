from rest_framework import serializers

from portal.apps.credentials.models import PublicCredentials


class CredentialSerializerList(serializers.ModelSerializer):
    public_key_credential = serializers.CharField(source='public_credential')
    public_key_expiration = serializers.DateTimeField(source='expiry_date')
    public_key_id = serializers.IntegerField(source='id', read_only=True)
    public_key_name = serializers.CharField(source='name')
    user_id = serializers.IntegerField(source='owner.id')

    class Meta:
        model = PublicCredentials
        fields = ['public_key_credential', 'public_key_expiration', 'public_key_id', 'public_key_name', 'user_id']


class CredentialSerializerDetail(serializers.ModelSerializer):
    created_date = serializers.DateTimeField(source='created')
    last_modified_by = serializers.CharField(source='modified_by')
    modified_date = serializers.DateTimeField(source='modified')
    public_key_credential = serializers.CharField(source='public_credential')
    public_key_expiration = serializers.DateTimeField(source='expiry_date')
    public_key_id = serializers.IntegerField(source='id', read_only=True)
    public_key_name = serializers.CharField(source='name')
    user_id = serializers.IntegerField(source='owner.id')

    class Meta:
        model = PublicCredentials
        fields = ['created_date', 'is_deleted', 'last_modified_by', 'modified_date', 'public_key_credential',
                  'public_key_expiration', 'public_key_id', 'public_key_name', 'user_id']

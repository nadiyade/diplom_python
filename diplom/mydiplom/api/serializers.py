from rest_framework import routers, serializers, viewsets
from mydiplom.models import MyUser, Claim, Comment, GENDER, CLAIM_PRIORITY, CLAIM_STATUS, CLAIM_THEME

'''Creating serializer from Models using ModelSerializer'''


class MyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        '''example of serialised model creation'''
        # fields = '__all__'
        '''example of API authentication model'''
        fields = ['username', 'last_name', 'first_name', 'email']


class ClaimSerializer(serializers.ModelSerializer):
    class Meta:
        model = Claim
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'


'''Creating serializer with writing all fields '''

# class CommentSerializer(serializers.Serializer):
#     id = serializers.IntegerField(read_only=True)
#     to_claim = serializers.PrimaryKeyRelatedField(read_only=True, many=True)  # from Claim
#     author = serializers.PrimaryKeyRelatedField(read_only=True, many=True)  # from MyUser
#     text = serializers.CharField(max_length=100000, allow_blank=False)
#     date_created = serializers.DateTimeField(read_only=True)
#     date_updated = serializers.DateTimeField(read_only=True)
#
#     def create(self, validated_data):
#         # Create and return a new `Comment` instance, given the validated data.
#         return Comment.objects.create(**validated_data)
#
#     def update(self, instance, validated_data):
#         # Update and return an existing `Comment` instance, given the validated data.
#         instance.to_claim = validated_data.get('to_claim', instance.to_claim)
#         instance.author = validated_data.get('author', instance.author)
#         instance.text = validated_data.get('text', instance.text)
#         instance.date_created = validated_data.get('date_created', instance.date_created)
#         instance.date_updated = validated_data.get('date_updated', instance.date_updated)
#         instance.save()
#         return instance

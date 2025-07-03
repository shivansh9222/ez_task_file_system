from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.signing import Signer, BadSignature
from django.http import FileResponse

from .models import UploadedFile, CustomUser
from .serializers import FileUploadSerializer, UserSerializer


signer = Signer()

class RegisterClient(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data

        # Reject registration if trying to use role OPS
        if data.get("role") != "CLIENT":
            return Response({"error": "Only CLIENT role is allowed to register via this API."}, status=403)

        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            encrypted_url = signer.sign(user.id)
            return Response({
                "message": "Registered successfully",
                "verify_url": f"/api/verify-email/{encrypted_url}/"
            }, status=201)
        return Response(serializer.errors, status=400)
    




class RegisterOPSUser(APIView):
    permission_classes = [AllowAny]  # You can change this to IsAdminUser for production

    def post(self, request):
        data = request.data

        if data.get("role") != "OPS":
            return Response({"error": "Only OPS role allowed here."}, status=403)

        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            user.is_active = True  # activate directly
            return Response({"message": "OPS user created successfully."}, status=201)
        return Response(serializer.errors, status=400)



class FileUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role != 'OPS':
            return Response({'error': 'Only OPS users allowed'}, status=403)
        file = request.FILES.get('file')
        if file.name.split('.')[-1] not in ['pptx', 'docx', 'xlsx']:
            return Response({'error': 'Invalid file type'}, status=400)
        UploadedFile.objects.create(file=file, uploaded_by=request.user)
        return Response({'message': 'File uploaded'}, status=201)



signer = Signer()

class DownloadFile(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, signed_id):
        try:
            file_id = signer.unsign(signed_id)
            file_obj = UploadedFile.objects.get(id=file_id)

            if request.user.role != 'CLIENT':
                return Response({'error': 'Unauthorized'}, status=403)

            response = FileResponse(file_obj.file.open('rb'), as_attachment=True)
            response['Content-Disposition'] = f'attachment; filename=\"{file_obj.file.name.split('/')[-1]}\"'
            return response

        except (UploadedFile.DoesNotExist, BadSignature):
            return Response({'error': 'Invalid or expired link'}, status=400)



class ListFiles(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'CLIENT':
            return Response({'error': 'Only CLIENT users allowed'}, status=403)

        files = UploadedFile.objects.all()
        return Response([
            {
                "id": file.id,
                "name": file.file.name,
                "download_link": f"/api/download/{signer.sign(file.id)}/"
            }
            for file in files
        ])

    


signer = Signer()

class VerifyEmail(APIView):
    permission_classes = [AllowAny]

    def get(self, request, signed_id):
        try:
            user_id = signer.unsign(signed_id)
            user = CustomUser.objects.get(id=user_id)
            user.is_active = True
            user.save()
            return Response({"message": "Email verified successfully"})
        except (CustomUser.DoesNotExist, BadSignature):
            return Response({"error": "Invalid or expired verification link"}, status=400)

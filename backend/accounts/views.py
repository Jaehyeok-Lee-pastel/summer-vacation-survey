from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from .models import UserProfile
import json
import traceback

@csrf_exempt
@require_http_methods(["GET"])
def api_status(request):
    """API 서버 상태 확인"""
    return JsonResponse({
        'status': 'OK',
        'message': '여름휴가 설문조사 API 서버가 정상 작동 중입니다!',
        'version': '1.0.0'
    })
    
    
@csrf_exempt
@require_http_methods(["POST"])
def api_register(request):
    """회원가입 API"""
    try:
        data = json.loads(request.body)
        
        # 필드 추출
        name = data.get('name', '').strip()
        userid = data.get('userid', '').strip()
        password = data.get('password', '').strip()
        password_confirm = data.get('password_confirm', '').strip()
        age = data.get('age', '').strip()
        email = data.get('email', '').strip()
        
        # 필수 필드 검증
        if not name:
            return JsonResponse({'success': False, 'message': '이름을 입력해주세요.'}, status=400)
        
        if not userid:
            return JsonResponse({'success': False, 'message': '아이디를 입력해주세요.'}, status=400)
            
        if not password:
            return JsonResponse({'success': False, 'message': '비밀번호를 입력해주세요.'}, status=400)
            
        if not password_confirm:
            return JsonResponse({'success': False, 'message': '비밀번호 확인을 입력해주세요.'}, status=400)
            
        if not age:
            return JsonResponse({'success': False, 'message': '나이를 입력해주세요.'}, status=400)
            
        if not email:
            return JsonResponse({'success': False, 'message': '이메일을 입력해주세요.'}, status=400)
        
        # 비밀번호 확인
        if password != password_confirm:
            return JsonResponse({'success': False, 'message': '비밀번호가 일치하지 않습니다.'}, status=400)
        
        # 나이 숫자 확인
        try:
            age_int = int(age)
            if age_int < 1 or age_int > 100:
                return JsonResponse({'success': False, 'message': '올바른 나이를 입력해주세요.'}, status=400)
        except ValueError:
            return JsonResponse({'success': False, 'message': '나이는 숫자로 입력해주세요.'}, status=400)
        
        # 아이디 중복 확인
        if User.objects.filter(username=userid).exists():
            return JsonResponse({'success': False, 'message': '이미 사용중인 아이디입니다.'}, status=400)
        
        # 이메일 중복 확인
        if User.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'message': '이미 사용중인 이메일입니다.'}, status=400)
        
        # 사용자 생성
        user = User.objects.create_user(
            username=userid,
            password=password,
            first_name=name,
            email=email
        )
        
        # 프로필 생성
        UserProfile.objects.create(
            user=user,
            age=age_int
        )
        
        return JsonResponse({
            'success': True,
            'message': '회원가입이 완료되었습니다.',
            'user': {
                'id': user.id,
                'username': user.username,
                'name': user.first_name,
                'email': user.email,
                'age': age_int
            }
        })
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': '잘못된 데이터 형식입니다.'}, status=400)
    except Exception as e:
        print("에러 발생:", str(e))            # 콘솔에 에러 메시지 출력
        traceback.print_exc()                 # 상세 스택트레이스 출력
        return JsonResponse({'success': False, 'message': f'서버 오류: {str(e)}'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_login(request):
    """로그인 API"""
    
    try:
        data = json.loads(request.body)
        userid = data.get('userid', '').strip()
        password = data.get('password', '').strip()

        # 필수 필드 검증
        if not userid:
            return JsonResponse({'success': False, 'message': '아이디를 입력해주세요.'}, status=400)
        if not password:
            return JsonResponse({'success': False, 'message': '비밀번호를 입력해주세요.'}, status=400)

        # 사용자 인증
        user = authenticate(username=userid, password=password)
        if user is None:
            return JsonResponse({'success': False, 'message': '아이디 또는 비밀번호가 올바르지 않습니다.'}, status=400)

        # 로그인 세션 생성
        login(request, user)

        # 프로필 정보 가져오기
        try:
            profile = user.userprofile  # UserProfile 연결되어 있어야 함
            age = profile.age
        except Exception:
            age = None

        return JsonResponse({
            'success': True,
            'message': f'{user.first_name}님, 로그인 성공!',
            'user': {
                'id': user.id,
                'username': user.username,
                'name': user.first_name,
                'email': user.email,
                'age': age
            }
        })

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': '잘못된 데이터 형식입니다.'}, status=400)
    except Exception as e:
        print("에러 발생:", str(e))
        traceback.print_exc()
        return JsonResponse({'success': False, 'message': f'서버 오류: {str(e)}'}, status=500)

# service/api.py
"""
FastAPI 기반 REST API 서버
Flutter 앱에서 사용할 수 있는 API 엔드포인트 제공
"""
import sys
from datetime import date
from typing import List, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# 프로젝트 루트를 path에 추가
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

# .env 파일 로드
load_dotenv(project_root / '.env')

# 데이터베이스 초기화
from db.database import init_database
init_database()

# FastAPI 앱 생성
app = FastAPI(
    title="시니어 운동 추천 API",
    description="시니어를 위한 운동 추천 및 커뮤니티 서비스 API",
    version="1.0.0"
)

# CORS 설정 (Flutter 앱에서 접근 가능하도록)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Pydantic 모델 정의 ====================

class UserProfileRequest(BaseModel):
    age_group: str  # "60-64", "65-69", "70-74", "75+"
    health_issues: List[str]
    goals: List[str]
    preference_env: str  # "indoor", "outdoor", "any"

class LocationRequest(BaseModel):
    lat: float
    lon: float

class RecommendRequest(BaseModel):
    user_profile: UserProfileRequest
    location: LocationRequest
    top_k: Optional[int] = 5

class RecommendationResponse(BaseModel):
    fac_id: str
    facility_name: str
    program_name: str
    sport_category: str
    distance_km: float
    intensity_level: str
    is_indoor: bool
    reason: str
    lat: float
    lon: float

class RecommendResponse(BaseModel):
    recommendations: List[RecommendationResponse]
    weather_info: dict

class UserCreateRequest(BaseModel):
    nickname: str
    age_group: str
    health_issues: List[str]
    goals: List[str]
    preference_env: str = "any"
    home_lat: Optional[float] = None
    home_lon: Optional[float] = None

class UserResponse(BaseModel):
    id: int
    nickname: str
    age_group: str
    health_issues: List[str]
    goals: List[str]
    preference_env: str
    home_lat: Optional[float]
    home_lon: Optional[float]

class JoinSessionRequest(BaseModel):
    user_id: int
    fac_id: str
    program_name: str
    session_date: str  # YYYY-MM-DD
    time_block: str  # "오전", "오후", "저녁"
    fac_name: str
    max_participants: int = 4

class JoinSessionResponse(BaseModel):
    status: str
    current_participants: int
    max_participants: int
    session_filled: bool
    session_id: Optional[int] = None
    message: Optional[str] = None

class ParticipantResponse(BaseModel):
    id: int
    nickname: str

class SessionParticipantsResponse(BaseModel):
    participants: List[ParticipantResponse]

class ExerciseVideoResponse(BaseModel):
    name: str
    체력항목: str
    운동도구: str
    신체부위: str
    혼자여부: str
    url: str
    info: str  # 포맷된 정보

class GroupExerciseVideosRequest(BaseModel):
    user_profile: Optional[UserProfileRequest] = None
    program_name: Optional[str] = None
    max_results: int = 5

class GroupExerciseVideosResponse(BaseModel):
    videos: List[ExerciseVideoResponse]

class NotificationRequest(BaseModel):
    user_id: str
    lat: Optional[float] = None  # 위치 정보 (기상청 API용)
    lon: Optional[float] = None
    has_chronic_disease: bool = False
    air_quality_risky: bool = False

class NotificationResponse(BaseModel):
    has_notification: bool
    message: Optional[str] = None
    exercise: Optional[ExerciseVideoResponse] = None
    weather_info: Optional[dict] = None

# ==================== API 엔드포인트 ====================

@app.get("/")
async def root():
    """API 상태 확인"""
    return {
        "status": "ok",
        "message": "시니어 운동 추천 API 서버가 실행 중입니다.",
        "version": "1.0.0"
    }

@app.get("/api/health")
async def health_check():
    """헬스 체크"""
    return {"status": "healthy"}

@app.post("/api/recommend", response_model=RecommendResponse)
async def get_recommendations(request: RecommendRequest):
    """
    날씨 기반 운동 추천
    
    사용자 프로필과 위치를 기반으로 날씨 정보를 조회하고
    운동/시설을 추천합니다.
    """
    try:
        from recommender.types import UserProfile, Location, WeatherInfo
        from recommender.pipeline import recommend
        from service.weather_client import fetch_weather
        
        # 타입 변환
        user_profile: UserProfile = {
            "age_group": request.user_profile.age_group,
            "health_issues": request.user_profile.health_issues,
            "goals": request.user_profile.goals,
            "preference_env": request.user_profile.preference_env,
        }
        
        user_location: Location = {
            "lat": request.location.lat,
            "lon": request.location.lon,
        }
        
        # 날씨 정보 조회
        weather_info = fetch_weather(user_location["lat"], user_location["lon"])
        
        # 추천 생성
        recommendations = recommend(
            user_profile=user_profile,
            user_location=user_location,
            weather_info=weather_info,
            top_k=request.top_k,
        )
        
        # 응답 변환
        recommendation_responses = [
            RecommendationResponse(**rec) for rec in recommendations
        ]
        
        return RecommendResponse(
            recommendations=recommendation_responses,
            weather_info={
                "temp": weather_info["temp"],
                "rain_prob": weather_info["rain_prob"],
                "pm10": weather_info["pm10"],
                "is_daytime": weather_info["is_daytime"],
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"추천 생성 중 오류 발생: {str(e)}")

@app.post("/api/user", response_model=UserResponse)
async def create_user(request: UserCreateRequest):
    """
    사용자 생성 (Flutter 앱 호환용)
    
    주의: Flutter 앱이 보내지 않는 필드들은 임시 기본값을 사용합니다.
    나중에 Flutter 앱을 수정하여 모든 필드를 전송하도록 권장합니다.
    """
    try:
        from db.user_repository import UserRepository
        
        repo = UserRepository()
        
        # Flutter 앱 데이터를 새 PostgreSQL 스키마로 변환
        # preference_env 변환: "indoor" -> "실내", "outdoor" -> "실외", "any" -> "둘 다"
        preference_map = {
            "indoor": "실내",
            "outdoor": "실외",
            "any": "둘 다"
        }
        preferred_location = preference_map.get(request.preference_env, "둘 다")
        
        # 임시 기본값 (Flutter 앱에서 전송하지 않는 필드)
        # ⚠️ 보안: password는 임시 기본값 사용 (나중에 Flutter 앱에서 받아야 함)
        default_password = "temp_password_123"  # 임시 비밀번호
        
        # age_group에서 birth_date 추정 불가능하므로 임시값 사용
        # Flutter 앱에서 birth_date를 직접 전송하도록 수정 필요
        default_birth_date = "500101"  # 임시 생년월일
        
        # 회원가입
        user = repo.create_user(
            password=default_password,  # ⚠️ 임시 - Flutter 앱에서 받아야 함
            name=request.nickname,
            birth_date=default_birth_date,  # ⚠️ 임시 - Flutter 앱에서 받아야 함
            gender="미지정",  # ⚠️ 임시 - Flutter 앱에서 받아야 함
            health_conditions=request.health_issues,
            exercise_goals=request.goals,
            preferred_location=preferred_location,
            phone="010-0000-0000",  # ⚠️ 임시 - Flutter 앱에서 받아야 함
            guardian_phone="010-0000-0000",  # ⚠️ 임시 - Flutter 앱에서 받아야 함
            address_road="주소 미입력",  # ⚠️ 임시 - Flutter 앱에서 받아야 함
            latitude=request.home_lat or 37.5665,
            longitude=request.home_lon or 126.9780,
        )
        
        # 비밀번호 해시 제거 후 반환
        user.pop('password_hash', None)
        
        # UserResponse 형식으로 변환 (기존 호환성 유지)
        return UserResponse(
            id=user['id'],
            nickname=user['name'],
            age_group=request.age_group,  # 원본 유지
            health_issues=user['health_conditions'],
            goals=user['exercise_goals'],
            preference_env=request.preference_env,  # 원본 유지
            home_lat=float(user['latitude']),
            home_lon=float(user['longitude']),
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"사용자 생성 중 오류 발생: {str(e)}")

@app.get("/api/users", response_model=List[dict])
async def get_all_users():
    """모든 사용자 정보 조회 (개발/테스트용)"""
    try:
        from db.user_repository import UserRepository
        from psycopg2.extras import RealDictCursor
        
        repo = UserRepository()
        
        # 모든 사용자 조회
        with repo._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT 
                        id, name, birth_date, gender,
                        health_conditions, exercise_goals, preferred_location,
                        phone, guardian_phone, address_road,
                        latitude, longitude, created_at
                    FROM users
                    ORDER BY created_at DESC
                """)
                results = cur.fetchall()
                users = []
                for row in results:
                    user_dict = dict(row)
                    # created_at을 문자열로 변환
                    if user_dict.get('created_at'):
                        user_dict['created_at'] = str(user_dict['created_at'])
                    users.append(user_dict)
                return users
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"사용자 조회 중 오류 발생: {str(e)}"
        )

@app.get("/api/user/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    """사용자 정보 조회 (ID로)"""
    try:
        from db.user_repository import UserRepository
        from psycopg2.extras import RealDictCursor
        
        repo = UserRepository()
        
        # ID로 조회
        with repo._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT 
                        id, name, birth_date, gender,
                        health_conditions, exercise_goals, preferred_location,
                        phone, guardian_phone, address_road,
                        latitude, longitude
                    FROM users
                    WHERE id = %s
                """, (user_id,))
                result = cur.fetchone()
                
                if not result:
                    raise HTTPException(
                        status_code=404,
                        detail="사용자를 찾을 수 없습니다."
                    )
                
                user = dict(result)
                
                # UserResponse 형식으로 변환
                return UserResponse(
                    id=user['id'],
                    nickname=user['name'],
                    age_group="60-64",  # 임시 (birth_date에서 계산 필요)
                    health_issues=user['health_conditions'],
                    goals=user['exercise_goals'],
                    preference_env=user['preferred_location'],  # 한글 -> 영어 변환 필요
                    home_lat=float(user['latitude']),
                    home_lon=float(user['longitude']),
                )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"사용자 조회 중 오류 발생: {str(e)}"
        )

@app.post("/api/community/join", response_model=JoinSessionResponse)
async def join_community_session(request: JoinSessionRequest):
    """
    커뮤니티 세션 참여
    
    사용자가 그룹 운동 세션에 참여합니다.
    """
    try:
        from service.community_client import join_session
        
        # 날짜 문자열을 date 객체로 변환
        session_date = date.fromisoformat(request.session_date)
        
        result = join_session(
            user_id=request.user_id,
            fac_id=request.fac_id,
            program_name=request.program_name,
            session_date=session_date,
            time_block=request.time_block,
            fac_name=request.fac_name,
            max_participants=request.max_participants,
        )
        
        return JoinSessionResponse(**result)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"잘못된 요청: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"세션 참여 중 오류 발생: {str(e)}")

@app.get("/api/community/session/{session_id}/participants", response_model=SessionParticipantsResponse)
async def get_session_participants(session_id: int):
    """세션 참여자 목록 조회"""
    try:
        from service.community_client import get_session_participants
        
        participants = get_session_participants(session_id)
        
        participant_responses = [
            ParticipantResponse(**p) for p in participants
        ]
        
        return SessionParticipantsResponse(participants=participant_responses)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"참여자 조회 중 오류 발생: {str(e)}")

@app.post("/api/exercise-videos/group", response_model=GroupExerciseVideosResponse)
async def get_group_exercise_videos(request: GroupExerciseVideosRequest):
    """
    함께 할 수 있는 운동 영상 추천
    
    커뮤니티 운동이 성사되었을 때 함께 할 수 있는 운동 영상을 추천합니다.
    """
    try:
        from service.exercise_video_client import (
            recommend_group_exercise_videos,
            format_video_info,
        )
        from recommender.types import UserProfile
        
        # UserProfile 변환
        user_profile = None
        if request.user_profile:
            user_profile: UserProfile = {
                "age_group": request.user_profile.age_group,
                "health_issues": request.user_profile.health_issues,
                "goals": request.user_profile.goals,
                "preference_env": request.user_profile.preference_env,
            }
        
        # 운동 영상 추천
        videos = recommend_group_exercise_videos(
            user_profile=user_profile,
            program_name=request.program_name,
            max_results=request.max_results,
        )
        
        # 응답 변환
        video_responses = []
        for video in videos:
            video_responses.append(ExerciseVideoResponse(
                name=video.get("Name", ""),
                체력항목=video.get("체력항목", ""),
                운동도구=video.get("운동도구", ""),
                신체부위=video.get("신체부위", ""),
                혼자여부=video.get("혼자여부", ""),
                url=video.get("url", ""),
                info=format_video_info(video),
            ))
        
        return GroupExerciseVideosResponse(videos=video_responses)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"운동 영상 추천 중 오류 발생: {str(e)}")

@app.post("/api/notification/exercise", response_model=NotificationResponse)
async def get_exercise_notification(request: NotificationRequest):
    """
    날씨 기반 운동 알림
    
    날씨가 위험할 때 실내 운동 영상을 추천하는 알림을 생성합니다.
    - 날씨 조회 → 위험 평가 → 위험하면 운동 영상 추천 → 알림 메시지 생성
    """
    try:
        from recommender.exercise_recommender import load_exercises, choose_exercise_for_today
        
        # 날씨 조회 및 위험 평가
        try:
            from service.weather_client import evaluate_weather_danger, fetch_kma_ultra_nowcast
            
            # 위치 정보 사용 (요청에 있으면 사용, 없으면 서울 기본값)
            lat = request.lat if request.lat is not None else 37.5665
            lon = request.lon if request.lon is not None else 126.9780
            
            weather = fetch_kma_ultra_nowcast(lat, lon)
            if not weather:
                # 날씨 조회 실패 시 알림 없음
                return NotificationResponse(
                    has_notification=False,
                    message=None,
                    exercise=None,
                    weather_info=None,
                )
            
            is_dangerous, weather_text = evaluate_weather_danger(
                weather,
                has_chronic_disease=request.has_chronic_disease,
                air_quality_risky=request.air_quality_risky,
            )
        except Exception as e:
            # 기상청 API 실패 시 알림 없음
            return NotificationResponse(
                has_notification=False,
                message=None,
                exercise=None,
                weather_info=None,
            )
        
        if not is_dangerous:
            # 위험하지 않으면 알림 없음
            return NotificationResponse(
                has_notification=False,
                message=None,
                exercise=None,
                weather_info={"status": "safe", "text": weather_text},
            )
        
        # 위험하면 운동 영상 추천
        exercises = load_exercises()
        if not exercises:
            return NotificationResponse(
                has_notification=False,
                message=None,
                exercise=None,
                weather_info={"status": "dangerous", "text": weather_text},
            )
        
        exercise = choose_exercise_for_today(
            exercises,
            user_id=request.user_id,
            today_date=None,  # 오늘 날짜 사용
        )
        
        # 알림 메시지 생성
        url = exercise.get("url", "")
        name = exercise.get("Name", "운동")
        message = (
            f"오늘은 {weather_text}입니다. "
            f"밖에 나가지 말고 집 안에서 운동하는 것이 좋겠어요. "
            f"{url} 이 운동({name})을 하는 것을 추천드릴게요."
        )
        
        # 응답 변환
        exercise_response = ExerciseVideoResponse(
            name=exercise.get("Name", ""),
            체력항목=exercise.get("체력항목", ""),
            운동도구=exercise.get("운동도구", ""),
            신체부위=exercise.get("신체부위", ""),
            혼자여부=exercise.get("혼자여부", ""),
            url=exercise.get("url", ""),
            info=f"체력항목: {exercise.get('체력항목', '')} | 도구: {exercise.get('운동도구', '')} | 부위: {exercise.get('신체부위', '')}",
        )
        
        return NotificationResponse(
            has_notification=True,
            message=message,
            exercise=exercise_response,
            weather_info={"status": "dangerous", "text": weather_text},
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"알림 생성 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



# service/group_exercise_video_client.py
"""
함께하는 운동을 위한 그룹 운동 영상 추천 클라이언트
커뮤니티 운동이 성사되었을 때 함께 할 수 있는 운동 영상을 추천합니다.
"""
from typing import List, Dict, Any, Optional
from recommender.types import UserProfile
from recommender.exercise_recommender import load_exercises  # 재사용


def filter_group_exercises(videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    혼자서 하는 운동이 아닌 영상만 필터링 (혼자여부 == "n").
    """
    return [v for v in videos if v.get("혼자여부", "y").lower() == "n"]


def recommend_group_exercise_videos(
    user_profile: Optional[UserProfile] = None,
    program_name: Optional[str] = None,
    max_results: int = 5,
) -> List[Dict[str, Any]]:
    """
    함께 운동이 성사되었을 때 추천할 운동 영상 리스트를 반환.
    
    Args:
        user_profile: 사용자 프로필 (선택사항, 추후 필터링에 활용)
        program_name: 추천된 프로그램 이름 (선택사항, 매칭에 활용)
        max_results: 최대 추천 개수
    
    Returns:
        함께 할 수 있는 운동 영상 리스트
    """
    # exercise_recommender의 load_exercises 함수 재사용
    all_videos = load_exercises()
    if not all_videos:
        return []
    
    # 혼자서 하는 운동이 아닌 것만 필터링
    group_videos = filter_group_exercises(all_videos)
    
    if not group_videos:
        return []
    
    # 사용자 프로필이나 프로그램 이름과 매칭되는 영상 우선 추천
    scored_videos = []
    
    for video in group_videos:
        score = 0.0
        
        # 프로그램 이름과 유사한 영상 이름 매칭 (간단한 키워드 매칭)
        if program_name:
            video_name = video.get("Name", "").lower()
            program_lower = program_name.lower()
            
            # 공통 키워드 체크
            common_keywords = ["줄", "협응", "스카프", "저글링", "함께", "동호회", "그룹"]
            for keyword in common_keywords:
                if keyword in video_name or keyword in program_lower:
                    score += 1.0
        
        # 사용자 목표와 체력항목 매칭
        if user_profile:
            goals = user_profile.get("goals", [])
            체력항목 = video.get("체력항목", "")
            
            # 목표와 체력항목 매핑
            goal_to_체력 = {
                "flexibility": "유연성",
                "strength": "근력/근지구력",
                "blood_pressure": "심폐지구력",
                "social": "협응력",
            }
            
            for goal in goals:
                if goal_to_체력.get(goal) == 체력항목:
                    score += 1.5
        
        scored_videos.append((score, video))
    
    # 점수 순으로 정렬 (점수가 높은 것 우선)
    scored_videos.sort(key=lambda x: x[0], reverse=True)
    
    # 상위 N개 반환
    recommended = [video for _, video in scored_videos[:max_results]]
    
    # 점수가 모두 0이거나 적은 경우, 랜덤하게 선택하기보다는 전체 반환 (최대 max_results)
    if not recommended or all(score == 0.0 for score, _ in scored_videos[:max_results]):
        # 점수 기반 추천이 안되면 전체 그룹 운동 중에서 반환
        return group_videos[:max_results]
    
    return recommended


def format_video_info(video: Dict[str, Any]) -> str:
    """
    운동 영상 정보를 포맷팅하여 반환.
    """
    name = video.get("Name", "운동 영상")
    체력항목 = video.get("체력항목", "")
    운동도구 = video.get("운동도구", "")
    신체부위 = video.get("신체부위", "")
    
    info_parts = []
    if 체력항목:
        info_parts.append(f"체력항목: {체력항목}")
    if 운동도구 and 운동도구 != "/":
        info_parts.append(f"도구: {운동도구}")
    if 신체부위 and 신체부위 not in ["/", "//"]:
        info_parts.append(f"부위: {신체부위}")
    
    info_str = " | ".join(info_parts) if info_parts else ""
    return info_str


def extract_youtube_video_id(url: str) -> Optional[str]:
    """
    YouTube URL에서 비디오 ID를 추출.
    https://www.youtube.com/watch?v=VIDEO_ID 형태 또는
    https://youtu.be/VIDEO_ID 형태를 지원.
    """
    if not url:
        return None
    
    # 오타 수정 (hhttps -> https)
    url = url.replace("hhttps://", "https://")
    
    # youtu.be 형식
    if "youtu.be/" in url:
        video_id = url.split("youtu.be/")[1].split("&")[0].split("?")[0]
        return video_id
    
    # youtube.com/watch?v= 형식
    if "youtube.com/watch" in url and "v=" in url:
        video_id = url.split("v=")[1].split("&")[0].split("#")[0]
        return video_id
    
    return None


def get_youtube_embed_url(url: str) -> Optional[str]:
    """
    YouTube URL을 embed URL로 변환.
    """
    video_id = extract_youtube_video_id(url)
    if video_id:
        return f"https://www.youtube.com/embed/{video_id}"
    return None


# Flutter 앱 - recommenDA

시니어 운동 추천 서비스의 Flutter 모바일 애플리케이션

## 개요

이 Flutter 앱은 시니어를 위한 맞춤형 운동 추천 서비스를 제공하는 모바일 애플리케이션입니다.

## 사전 요구사항

- Flutter SDK 설치
- Dart SDK 설치
- Android Studio 또는 Xcode (플랫폼별 개발용)

## 환경 설정

### 1. KAKAO API 키 발급 및 설정

1. [Kakao Developers](https://developers.kakao.com/)에서 애플리케이션 등록
2. 다음 설정을 완료해야 합니다:
   - **IP 주소 등록**: 앱에서 사용할 IP 주소를 플랫폼 설정에 등록
   - **카카오맵 사용 설정**: 카카오맵 API 사용 권한 활성화

3. `.env` 파일 생성 및 설정:
   ```
   KAKAO_API=발급받은_카카오_API_키
   ```
   
   > **참고**: `.env` 파일은 `example1` 폴더 내에 위치해야 합니다.

## 구현된 기능

### 1. 회원가입
- 사용자 정보 입력 및 회원가입 기능

### 2. 위치 확인
플랫폼별 위치 확인 방식:
- **Android**: 위치 권한 설정 필요. 위치가 확인되지 않는 경우 주소 검색 기능 제공
- **iOS**: 위치 권한 설정 필요 (추가 확인 필요)
- **Chrome (웹)**: 위치 API를 통해 자동으로 위치 정보 수집. 주소 검색 기능은 제공되지 않음

### 3. 메인 화면
다음 정보를 표시합니다:
- 현재 날씨 정보
- 추천 운동 장소
- 추천 운동 프로그램

## 실행 방법

1. 의존성 설치:
```bash
flutter pub get
```

2. 앱 실행:
```bash
# Android
flutter run

# iOS
flutter run

# 웹
flutter run -d chrome
```

## 개발 참고 자료

Flutter 개발을 시작하는 경우 다음 자료를 참고하세요:

- [Flutter 공식 문서](https://docs.flutter.dev/)
- [Flutter 첫 앱 만들기](https://docs.flutter.dev/get-started/codelab)
- [Flutter 샘플 코드](https://docs.flutter.dev/cookbook)

## 문제 해결

### 위치 정보가 표시되지 않는 경우
- Android: 앱 설정에서 위치 권한을 확인하세요
- iOS: 설정 > 개인정보 보호 > 위치 서비스에서 앱 권한을 확인하세요
- 웹: 브라우저에서 위치 접근 권한을 허용해야 합니다

### 카카오맵이 표시되지 않는 경우
- `.env` 파일에 올바른 KAKAO_API 키가 설정되어 있는지 확인
- Kakao Developers 콘솔에서 카카오맵 API 사용 설정이 활성화되어 있는지 확인
- IP 주소가 올바르게 등록되어 있는지 확인

import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:google_fonts/google_fonts.dart'; 
import 'package:flutter_naver_map/flutter_naver_map.dart'; // [필수] 지도 패키지
import 'signup.dart'; 
import 'notification.dart'; 

void main() async {
  // 1. 플러터 엔진 초기화 (필수)
  WidgetsFlutterBinding.ensureInitialized();
  
  // 2. 환경변수 로드
  try {
    await dotenv.load(fileName: ".env");
  } catch (e) {
    print("⚠️ .env 로드 실패 (무시): $e");
  }

  // 3. [복구됨] 네이버 지도 SDK 초기화 (이게 꼭 있어야 합니다!)
  try {
    await NaverMapSdk.instance.initialize(
      // 1순위: .env 파일에서 가져오기
      // 2순위: .env가 안 되면 여기에 직접 '클라이언트 ID'를 문자열로 넣으세요!
      clientId: dotenv.env['NAVER_MAP_CLIENT_ID'] ?? '!!', 
      onAuthFailed: (ex) {
        print("********* 네이버 지도 인증 실패: $ex *********");
      },
    );
  } catch (e) {
    print("네이버 지도 초기화 중 에러 발생: $e");
  }

  // 4. 알림 서비스 등 기타 초기화 (비동기로 실행)
  _initServices(); 

  // 5. 앱 실행
  runApp(const MyApp());
}

// 기타 서비스 초기화 함수
Future<void> _initServices() async {
  try {
    final notificationService = NotificationService();
    await notificationService.init();
  } catch (e) {
    print("알림 초기화 실패: $e");
  }
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Senior Health App',
      theme: ThemeData(
        useMaterial3: true,
        scaffoldBackgroundColor: const Color(0xFFF1F8E9),
        textTheme: GoogleFonts.notoSansKrTextTheme(
          Theme.of(context).textTheme,
        ),
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF2E7D32),
          primary: const Color(0xFF2E7D32),
          surface: const Color(0xFFF1F8E9),
        ),
        appBarTheme: AppBarTheme(
          backgroundColor: const Color(0xFF2E7D32),
          foregroundColor: Colors.white,
          centerTitle: true,
          elevation: 0,
          titleTextStyle: TextStyle(
            fontFamily: GoogleFonts.notoSansKr().fontFamily,
            fontSize: 22,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
      ),
      home: const SignUpPage(title: '회원가입'),
    );
  }
}
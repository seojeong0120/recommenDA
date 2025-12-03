import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:google_fonts/google_fonts.dart'; 
import 'package:flutter_naver_map/flutter_naver_map.dart'; 
import 'login_screen.dart'; // [변경] 로그인 화면 import
import 'notification.dart'; 

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  try {
    await dotenv.load(fileName: ".env");
  } catch (e) {
    print("⚠️ .env 로드 실패 (무시): $e");
  }

  _initServices(); 

  runApp(const MyApp());
}

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
      // [변경] 앱 시작 시 로그인 화면 표시
      home: const LoginScreen(),
    );
  }
}
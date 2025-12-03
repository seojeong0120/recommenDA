import 'package:flutter/material.dart';
import 'signup.dart';
import 'home_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final TextEditingController _idController = TextEditingController();
  final TextEditingController _pwController = TextEditingController();

  // 로그인 로직 (추후 API 연동 필요)
  void _login() {
    final id = _idController.text;
    final pw = _pwController.text;

    if (id.isEmpty || pw.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('아이디와 비밀번호를 입력해주세요.')),
      );
      return;
    }

    // [임시] 서버에 로그인 API가 아직 없으므로, 일단 더미 데이터로 홈으로 이동시킵니다.
    // 나중에 실제 로그인 API (/api/login)를 호출하여 사용자 정보를 받아와야 합니다.
    print("로그인 시도 - ID: $id, PW: $pw");
    
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(
        builder: (context) => HomeScreen(
          // 실제로는 서버에서 받은 유저 정보를 넣어야 합니다.
          userProfile: {
            "nickname": "사용자", 
            "age_group": "65-69", 
            "health_issues": [], 
            "goals": ["체력 증진"],
            "preference_env": "any"
          },
          currentLat: 37.5665,
          currentLon: 126.9780,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final primaryColor = Theme.of(context).colorScheme.primary;

    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Icon(Icons.favorite_rounded, size: 80, color: Colors.teal),
              const SizedBox(height: 20),
              const Text(
                "시니어 건강 지킴이",
                style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: Colors.teal),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 50),

              // 아이디 입력
              TextField(
                controller: _idController,
                decoration: InputDecoration(
                  labelText: "아이디",
                  prefixIcon: const Icon(Icons.person),
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                ),
              ),
              const SizedBox(height: 16),

              // 비밀번호 입력
              TextField(
                controller: _pwController,
                obscureText: true,
                decoration: InputDecoration(
                  labelText: "비밀번호",
                  prefixIcon: const Icon(Icons.lock),
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                ),
              ),
              const SizedBox(height: 30),

              // 로그인 버튼
              ElevatedButton(
                onPressed: _login,
                style: ElevatedButton.styleFrom(
                  backgroundColor: primaryColor,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  textStyle: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                child: const Text("로그인"),
              ),
              const SizedBox(height: 16),

              // 회원가입 버튼
              OutlinedButton(
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => const SignUpPage(title: "회원가입")),
                  );
                },
                style: OutlinedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  side: BorderSide(color: primaryColor),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  textStyle: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                child: const Text("회원가입"),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
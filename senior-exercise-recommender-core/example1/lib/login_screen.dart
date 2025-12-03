<<<<<<< HEAD
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
=======
import 'package:flutter/material.dart';
>>>>>>> 6f0b9ce7f2b49bf894db922eed57eccd4949f933
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
<<<<<<< HEAD
  bool _isLoading = false;

  // 로그인 함수
  Future<void> _login() async {
=======

  // 로그인 로직 (추후 API 연동 필요)
  void _login() {
>>>>>>> 6f0b9ce7f2b49bf894db922eed57eccd4949f933
    final id = _idController.text;
    final pw = _pwController.text;

    if (id.isEmpty || pw.isEmpty) {
<<<<<<< HEAD
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('아이디와 비밀번호를 입력해주세요.')));
      return;
    }

    setState(() => _isLoading = true);

    // [주의] 현재 api.py에 /api/login이 없으면 404 에러가 날 수 있습니다.
    const String apiUrl = "http://10.0.2.2:8000/api/login";

    try {
      final response = await http.post(
        Uri.parse(apiUrl),
        headers: {"Content-Type": "application/json; charset=UTF-8"},
        body: jsonEncode({
          "username": id, // 서버가 LoginRequest에서 username을 받는다고 가정
          "password": pw,
        }),
      );

      if (response.statusCode == 200) {
        final userData = jsonDecode(utf8.decode(response.bodyBytes));
        if (!mounted) return;
        
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(
            builder: (context) => HomeScreen(
              userProfile: userData,
              currentLat: userData['home_lat'] ?? 37.5665,
              currentLon: userData['home_lon'] ?? 126.9780,
            ),
          ),
        );
      } else {
        throw Exception("로그인 실패: 아이디/비밀번호를 확인하세요.");
      }
    } catch (e) {
      print("로그인 에러: $e");
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text("로그인 실패 (서버 확인 필요)")));
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
=======
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
>>>>>>> 6f0b9ce7f2b49bf894db922eed57eccd4949f933
  }

  @override
  Widget build(BuildContext context) {
<<<<<<< HEAD
=======
    final primaryColor = Theme.of(context).colorScheme.primary;

>>>>>>> 6f0b9ce7f2b49bf894db922eed57eccd4949f933
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
<<<<<<< HEAD
              const Text("시니어 건강 지킴이", style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: Colors.teal), textAlign: TextAlign.center),
              const SizedBox(height: 50),

              TextField(
                controller: _idController,
                decoration: InputDecoration(labelText: "아이디 (전화번호)", prefixIcon: const Icon(Icons.person), border: OutlineInputBorder(borderRadius: BorderRadius.circular(12))),
              ),
              const SizedBox(height: 16),

              TextField(
                controller: _pwController,
                obscureText: true,
                decoration: InputDecoration(labelText: "비밀번호", prefixIcon: const Icon(Icons.lock), border: OutlineInputBorder(borderRadius: BorderRadius.circular(12))),
              ),
              const SizedBox(height: 30),

              SizedBox(
                height: 55,
                child: ElevatedButton(
                  onPressed: _isLoading ? null : _login,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Theme.of(context).colorScheme.primary,
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    textStyle: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  child: _isLoading ? const CircularProgressIndicator(color: Colors.white) : const Text("로그인"),
=======
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
>>>>>>> 6f0b9ce7f2b49bf894db922eed57eccd4949f933
                ),
              ),
              const SizedBox(height: 16),

<<<<<<< HEAD
              OutlinedButton(
                onPressed: () {
                  Navigator.push(context, MaterialPageRoute(builder: (context) => const SignUpPage(title: "회원가입")));
                },
                style: OutlinedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  side: BorderSide(color: Theme.of(context).colorScheme.primary),
=======
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
>>>>>>> 6f0b9ce7f2b49bf894db922eed57eccd4949f933
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
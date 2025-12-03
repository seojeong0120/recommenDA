import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
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
  bool _isLoading = false;

  // 로그인 함수
  Future<void> _login() async {
    final id = _idController.text;
    final pw = _pwController.text;

    if (id.isEmpty || pw.isEmpty) {
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
  }

  @override
  Widget build(BuildContext context) {
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
                ),
              ),
              const SizedBox(height: 16),

              OutlinedButton(
                onPressed: () {
                  Navigator.push(context, MaterialPageRoute(builder: (context) => const SignUpPage(title: "회원가입")));
                },
                style: OutlinedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  side: BorderSide(color: Theme.of(context).colorScheme.primary),
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
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:http/http.dart' as http;
import 'package:kpostal/kpostal.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'home_screen.dart';

class UserLocationScreen extends StatefulWidget {
  final String userId; // [신규]
  final String password; // [신규]
  final String name;
  final String birthdate;
  final String gender;
  final List<String> healthIssues;
  final List<String> goals;
  final String preference;

  const UserLocationScreen({
    super.key,
    required this.userId,
    required this.password,
    required this.name,
    required this.birthdate,
    required this.gender,
    required this.healthIssues,
    required this.goals,
    required this.preference,
  });

  @override
  State<UserLocationScreen> createState() => _UserLocationScreenState();
}

class _UserLocationScreenState extends State<UserLocationScreen> {
  String _address = "위치를 찾는 중입니다...";
  bool _isLoading = true;
  bool _isLocationFound = false;
  double? _lat;
  double? _lon;

  final String _kakaoRestApiKey = dotenv.env['KAKAO_API_KEY'] ?? "";

  @override
  void initState() {
    super.initState();
    _getCurrentLocation();
  }

  Future<void> _getCurrentLocation() async {
    LocationPermission permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) {
        setState(() { _address = "위치 권한이 필요합니다."; _isLoading = false; });
        return;
      }
    }
    try {
      Position position = await Geolocator.getCurrentPosition(
          desiredAccuracy: LocationAccuracy.high,
          timeLimit: const Duration(seconds: 5)
      );
      _lat = position.latitude;
      _lon = position.longitude;
      await _getAddressFromKakao(position.latitude, position.longitude);
    } catch (e) {
      setState(() { _address = "위치 확인 실패."; _isLoading = false; });
    }
  }

  Future<void> _getAddressFromKakao(double lat, double lng) async {
    String url = "https://dapi.kakao.com/v2/local/geo/coord2address.json?x=$lng&y=$lat";
    try {
      var response = await http.get(Uri.parse(url), headers: {"Authorization": "KakaoAK $_kakaoRestApiKey"});
      if (response.statusCode == 200) {
        var documents = jsonDecode(response.body)['documents'];
        if (documents != null && documents.length > 0) {
          var addressInfo = documents[0]['road_address'] ?? documents[0]['address'];
          setState(() {
            _address = "${addressInfo['address_name']} ${addressInfo['building_name'] ?? ''}";
            _isLoading = false;
            _isLocationFound = true;
          });
        }
      }
    } catch (e) { print(e); setState(() => _isLoading = false); }
  }

  Future<void> _searchAddress() async {
    Kpostal? result = await Navigator.push(context, MaterialPageRoute(builder: (_) => KpostalView()));
    if (result != null) {
      setState(() {
        _address = result.address;
        _lat = result.latitude;
        _lon = result.longitude;
        _isLocationFound = true;
        _isLoading = false;
      });
    }
  }

  String _calculateAgeGroup(String birth) {
    int yearPrefix = int.parse(birth.substring(0, 2));
    int currentYear = DateTime.now().year;
    int birthYear = (yearPrefix > 25) ? 1900 + yearPrefix : 2000 + yearPrefix;
    int age = currentYear - birthYear;

    if (age >= 75) return "75+";
    if (age >= 70) return "70-74";
    if (age >= 65) return "65-69";
    return "60-64"; 
  }

  String _mapPreferenceToApi(String pref) {
    if (pref == "실내") return "indoor";
    if (pref == "실외") return "outdoor";
    return "any";
  }

// ... (위쪽 import는 그대로) ...

  // 회원가입 API 호출 함수
  Future<void> _registerAndGoHome() async {
    // 에뮬레이터용 주소 (10.0.2.2)
    const String apiUrl = "http://10.0.2.2:8000/api/user"; 
    
    setState(() => _isLoading = true);

    try {
      final Map<String, dynamic> requestBody = {
        "username": widget.userId,
        "password": widget.password,
        "nickname": widget.name,
        "age_group": _calculateAgeGroup(widget.birthdate),
        "health_issues": widget.healthIssues,
        "goals": widget.goals,
        "preference_env": _mapPreferenceToApi(widget.preference),
        "home_lat": _lat ?? 37.5665,
        "home_lon": _lon ?? 126.9780,
      };

      print("보내는 데이터: $requestBody");

      final response = await http.post(
        Uri.parse(apiUrl),
        headers: {
          // [핵심] 여기서 UTF-8임을 명시하면, body가 String이어도 알아서 잘 처리해줍니다.
          "Content-Type": "application/json; charset=UTF-8", 
        },
        // [변경] utf8.encode()를 제거하고, 그냥 json string을 보냅니다.
        body: jsonEncode(requestBody), 
      );

      // --- 응답 처리 ---
      if (response.statusCode == 200) {
        // 한글 깨짐 방지를 위해 bodyBytes를 decode 합니다.
        final userData = jsonDecode(utf8.decode(response.bodyBytes));
        
        if (!mounted) return;
        
        showDialog(
          context: context,
          barrierDismissible: false,
          builder: (context) => AlertDialog(
            title: const Text("환영합니다!", style: TextStyle(fontWeight: FontWeight.bold)),
            content: const Text("등록이 완료되었습니다.\n운동 추천을 시작합니다."),
            actions: [
              TextButton(
                onPressed: () {
                  Navigator.pop(context);
                  Navigator.pushAndRemoveUntil(
                    context,
                    MaterialPageRoute(
                      builder: (context) => HomeScreen(
                        userProfile: userData,
                        currentLat: _lat ?? 37.5665,
                        currentLon: _lon ?? 126.9780,
                      ),
                    ),
                    (route) => false,
                  );
                },
                child: const Text("시작하기", style: TextStyle(fontWeight: FontWeight.bold, color: Colors.teal)),
              ),
            ],
          ),
        );
      } else {
        // 에러 메시지도 한글 디코딩 시도
        String errorDetail = response.body;
        try {
           errorDetail = utf8.decode(response.bodyBytes);
        } catch (_) {}
        throw Exception("서버 에러 (${response.statusCode}): $errorDetail");
      }
    } catch (e) {
      print("가입 에러: $e");
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("오류가 발생했습니다. 다시 시도해주세요.")),
      );
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }
// ... (나머지 코드는 그대로) ...
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("거주지 설정")),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          children: [
            const Text("거주지가 맞으신가요?", style: TextStyle(fontSize: 26, fontWeight: FontWeight.bold)),
            const SizedBox(height: 30),
            Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(border: Border.all(color: Colors.teal), borderRadius: BorderRadius.circular(16)),
              child: Column(
                children: [
                   _isLoading ? const CircularProgressIndicator() : const Icon(Icons.location_on, size: 50, color: Colors.teal),
                   const SizedBox(height: 10),
                   Text(_address, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold), textAlign: TextAlign.center),
                ],
              ),
            ),
            const Spacer(),
            Row(children: [
              Expanded(child: OutlinedButton(onPressed: _searchAddress, child: const Text("아니요", style: TextStyle(fontSize: 18)))),
              const SizedBox(width: 10),
              Expanded(flex: 2, child: ElevatedButton(
                onPressed: (_isLocationFound && !_isLoading) ? _registerAndGoHome : null,
                style: ElevatedButton.styleFrom(backgroundColor: Colors.teal, foregroundColor: Colors.white),
                child: const Text("가입 끝내기", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
              )),
            ]),
            const SizedBox(height: 20),
          ],
        ),
      ),
    );
  }
}
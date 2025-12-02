import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:http/http.dart' as http;
import 'package:kpostal/kpostal.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'home_screen.dart';

class UserLocationScreen extends StatefulWidget {
  final String name;
  final String birthdate;
  final String gender;
  final List<String> healthIssues; // 복수 선택 리스트
  final List<String> goals;        // 복수 선택 리스트
  final String preference;         // [추가됨] 선호 장소 (실내, 실외, 둘 다)

  const UserLocationScreen({
    super.key,
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
      Position position = await Geolocator.getCurrentPosition(desiredAccuracy: LocationAccuracy.high);
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

  // [중요] 한글 장소 선호도를 API용 영어 코드로 변환
  String _mapPreferenceToApi(String pref) {
    if (pref == "실내") return "indoor";
    if (pref == "실외") return "outdoor";
    return "any"; // "둘 다" 또는 예외 상황
  }

  // 회원가입 API 호출
  Future<void> _registerAndGoHome() async {
    const String apiUrl = "http://10.0.2.2:8000/api/user"; 
    
    setState(() => _isLoading = true);

    try {
      // 1. 데이터 준비
      final Map<String, dynamic> requestBody = {
        "nickname": widget.name,
        "age_group": _calculateAgeGroup(widget.birthdate),
        "health_issues": widget.healthIssues, // 리스트 그대로 전송
        "goals": widget.goals,                // 리스트 그대로 전송
        "preference_env": _mapPreferenceToApi(widget.preference), // 변환해서 전송
        "home_lat": _lat ?? 37.5665,
        "home_lon": _lon ?? 126.9780,
      };

      print("보내는 데이터: $requestBody"); // 디버깅용

      // 2. 서버 전송
      final response = await http.post(
        Uri.parse(apiUrl),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode(requestBody),
      );

      if (response.statusCode == 200) {
        final userData = jsonDecode(utf8.decode(response.bodyBytes));
        
        if (!mounted) return;
        
        // 성공 팝업
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
        throw Exception("서버 에러: ${response.statusCode} / ${response.body}");
      }
    } catch (e) {
      print("가입 에러: $e");
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("오류가 발생했습니다: $e")));
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

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
                child: const Text("등록 끝내기", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
              )),
            ]),
            const SizedBox(height: 20),
          ],
        ),
      ),
    );
  }
}
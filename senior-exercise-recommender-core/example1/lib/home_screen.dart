import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'map_screen.dart';

class HomeScreen extends StatefulWidget {
  final Map<String, dynamic> userProfile; 
  final double currentLat;
  final double currentLon;

  const HomeScreen({
    super.key,
    required this.userProfile,
    required this.currentLat,
    required this.currentLon,
  });

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  String _exerciseName = "분석 중...";
  String _placeName = "위치 확인 중...";
  String _weatherText = "정보 로딩 중...";
  String _reason = "";
  
  // 추천된 장소의 좌표 (기본값: 연세대)
  double _targetLat = 37.5642135;
  double _targetLon = 126.936660;

  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _fetchRecommendation();
  }

  Future<void> _fetchRecommendation() async {
    const String apiUrl = "http://10.0.2.2:8000/api/recommend";

    try {
      final Map<String, dynamic> requestBody = {
        "user_profile": {
          "age_group": widget.userProfile['age_group'],
          "health_issues": widget.userProfile['health_issues'] ?? [],
          "goals": widget.userProfile['goals'] ?? ["체력 증진"],
          "preference_env": widget.userProfile['preference_env'] ?? "any"
        },
        "location": {
          "lat": widget.currentLat,
          "lon": widget.currentLon
        },
        "top_k": 1
      };

      final response = await http.post(
        Uri.parse(apiUrl),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode(requestBody),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(utf8.decode(response.bodyBytes));
        final recommendations = data['recommendations'] as List;
        final weather = data['weather_info'];

        if (recommendations.isNotEmpty) {
          final topRec = recommendations[0];
          setState(() {
            // [수정] null이면 빈 문자열로 처리해서 아래 UI 로직이 돌도록 함
            _exerciseName = topRec['program_name'] ?? ""; 
            _placeName = topRec['facility_name'] ?? "추천 장소";   
            _reason = topRec['reason'] ?? "";
            
            // 좌표 정보 업데이트 (서버 응답에 포함되어 있다면)
            // _targetLat = topRec['lat'] ?? 37.5642; 
            // _targetLon = topRec['lon'] ?? 126.9366;
            
            String rain = (weather['rain_prob'] > 30) ? "비" : "맑음";
            _weatherText = "기온 ${weather['temp']}°C, $rain";
            
            _isLoading = false;
          });
        } else {
          setState(() {
            _exerciseName = ""; // 데이터 없음 처리
            _placeName = "주변 공원";
            _reason = "조건에 맞는 시설을 찾지 못했습니다.";
            _isLoading = false;
          });
        }
      } else {
        throw Exception("서버 오류: ${response.statusCode}");
      }
    } catch (e) {
      print("추천 실패: $e");
      setState(() {
        _exerciseName = ""; 
        _placeName = "주변 공원";
        _weatherText = "서버 연결 실패";
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final primaryGreen = Theme.of(context).colorScheme.primary;

    return Scaffold(
      appBar: AppBar(
        title: const Text("오늘의 운동", style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: primaryGreen,
        foregroundColor: Colors.white,
        automaticallyImplyLeading: false,
      ),
      body: _isLoading 
        ? const Center(child: CircularProgressIndicator()) 
        : SingleChildScrollView(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(
                  "${widget.userProfile['nickname']}님 안녕하세요!\n오늘도 건강한 하루 되세요.",
                  style: const TextStyle(fontSize: 26, fontWeight: FontWeight.bold, height: 1.4),
                ),
                const SizedBox(height: 30),
                
                // 날씨 카드
                Container(
                  padding: const EdgeInsets.all(24),
                  decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(20)),
                  child: Row(children: [
                    const Icon(Icons.wb_sunny_rounded, size: 48, color: Colors.orange),
                    const SizedBox(width: 20),
                    Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                      const Text("오늘의 날씨", style: TextStyle(color: Colors.grey)),
                      Text(_weatherText, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
                    ])),
                  ]),
                ),
                
                const SizedBox(height: 30),
                
                // 운동 추천 카드
                Container(
                  padding: const EdgeInsets.all(24),
                  decoration: BoxDecoration(
                    color: primaryGreen,
                    borderRadius: BorderRadius.circular(24),
                  ),
                  child: Column(children: [
                    const Icon(Icons.directions_walk, size: 80, color: Colors.white),
                    const SizedBox(height: 20),

                    // [수정된 부분] 운동 이름 유무에 따라 문구 변경
                    if (_exerciseName.isEmpty)
                      // 운동 이름이 없을 때
                      Text(
                        "오늘은 '$_placeName'에\n방문해보세요.",
                        style: const TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: Colors.white),
                        textAlign: TextAlign.center,
                      )
                    else ...[
                      // 운동 이름이 있을 때 (기존 방식)
                      Text(
                        "'$_placeName'에서", 
                        style: const TextStyle(fontSize: 22, color: Colors.white70),
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 8),
                      Text(
                        "'$_exerciseName'을(를)\n해보세요.", 
                        style: const TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: Colors.white),
                        textAlign: TextAlign.center,
                      ),
                    ],

                    const SizedBox(height: 20),
                    if (_reason.isNotEmpty)
                      Text(_reason, style: const TextStyle(fontSize: 16, color: Colors.white70), textAlign: TextAlign.center),
                    
                    const SizedBox(height: 30),

                    // [지도 버튼] 네이버 지도 화면으로 이동
                    ElevatedButton.icon(
                      onPressed: () {
                         Navigator.push(context, MaterialPageRoute(builder: (context) => MapScreen(
                           placeName: _placeName, 
                           latitude: _targetLat, // 추천 장소의 좌표 전달
                           longitude: _targetLon,
                         )));
                      },
                      icon: const Icon(Icons.map, color: Colors.green),
                      label: const Text("운동 장소 지도 보기", style: TextStyle(color: Colors.green, fontWeight: FontWeight.bold)),
                      style: ElevatedButton.styleFrom(backgroundColor: Colors.white),
                    ),
                  ]),
                ),
              ],
            ),
          ),
    );
  }
}
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
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _fetchRecommendation();
  }

  Future<void> _fetchRecommendation() async {
    const String apiUrl = "http://10.0.2.2:8000/api/recommend";

    try {
      // api.py의 RecommendRequest 모델에 맞춘 데이터 구조
      final Map<String, dynamic> requestBody = {
        "user_profile": {
          "age_group": widget.userProfile['age_group'],
          "health_issues": widget.userProfile['health_issues'],
          "goals": widget.userProfile['goals'],
          "preference_env": widget.userProfile['preference_env']
        },
        "location": {
          "lat": widget.currentLat,
          "lon": widget.currentLon
        },
        "top_k": 1
      };

      print("추천 요청 데이터: $requestBody");

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
            _exerciseName = topRec['program_name']; 
            _placeName = topRec['facility_name'];   
            _reason = topRec['reason'];             
            
            // 날씨 텍스트 (예: 기온 20도, 비 올 확률 있음)
            String rain = (weather['rain_prob'] > 30) ? "비" : "맑음";
            _weatherText = "기온 ${weather['temp']}°C, $rain";
            
            _isLoading = false;
          });
        } else {
        // 추천 결과 0개일 때...
        print("주변 운동 시설이 없어 추천할 수 없습니다. 장소를 바꿔보세요.");
        setState(() {
          _exerciseName = "가벼운 산책";
          _placeName = "주변 공원";
          _weatherText = "서버 연결 실패";
          _reason = "주변 운동 시설이 없어 추천할 수 없습니다. 장소를 바꿔보세요.";
          _isLoading = false;
        });
      } 
      } else {
        throw Exception("서버 오류: ${response.statusCode}");
      }
    } catch (e) {
      print("추천 실패 에러 : $e");
      setState(() {
        _exerciseName = "추천 실패";
        _placeName = "검색 실패";
        _weatherText = "날씨 정보 없음";
        _reason = "서버 연결 실패";
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("오늘의 운동", style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: Theme.of(context).colorScheme.primary,
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
                // 운동 카드
                Container(
                  padding: const EdgeInsets.all(24),
                  decoration: BoxDecoration(
                    color: Theme.of(context).colorScheme.primary,
                    borderRadius: BorderRadius.circular(24),
                  ),
                  child: Column(children: [
                    const Icon(Icons.directions_walk, size: 80, color: Colors.white),
                    const SizedBox(height: 20),
                    Text("'$_placeName'에서", style: const TextStyle(fontSize: 22, color: Colors.white70)),
                    Text("'$_exerciseName'을(를)\n해보세요.", style: const TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: Colors.white), textAlign: TextAlign.center),
                    const SizedBox(height: 20),
                    Text(_reason, style: const TextStyle(fontSize: 16, color: Colors.white70), textAlign: TextAlign.center),
                    const SizedBox(height: 30),
                    ElevatedButton.icon(
                      onPressed: () {
                         Navigator.push(context, MaterialPageRoute(builder: (context) => MapScreen(
                           placeName: _placeName, 
                           latitude: widget.currentLat, 
                           longitude: widget.currentLon
                         )));
                      },
                      icon: const Icon(Icons.map), label: const Text("지도 보기"),
                    ),
                  ]),
                ),
              ],
            ),
          ),
    );
  }
}
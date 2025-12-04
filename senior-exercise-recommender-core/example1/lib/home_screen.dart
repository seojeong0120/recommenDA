import 'dart:convert';
import 'dart:math';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'map_screen.dart';
import 'home_exercise_screen.dart';
import 'login_screen.dart';

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
  
  double _targetLat = 37.5665;
  double _targetLon = 126.9780;

  Map<String, dynamic>? _homeExerciseData; 

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
        "top_k": 5 
      };

      final response = await http.post(
        Uri.parse(apiUrl),
        headers: {"Content-Type": "application/json; charset=UTF-8"},
        body: jsonEncode(requestBody),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(utf8.decode(response.bodyBytes));
        
        final recommendations = data['recommendations'] as List;
        final weather = data['weather_info'];
        
        final homeVideos = data['exercise_videos'] as List?;

        setState(() {
          // 1. 날씨 정보
          String rain = (weather['rain_prob'] > 30) ? "비" : "맑음";
          _weatherText = "기온 ${weather['temp']}°C, $rain";

          // 2. 실내 운동 데이터
          if (homeVideos != null && homeVideos.isNotEmpty) {
            _homeExerciseData = homeVideos[0];
          } else {
            _homeExerciseData = null;
          }

          // 3. 시설 추천 데이터 (랜덤 선택)
          if (recommendations.isNotEmpty) {
            final randomIndex = Random().nextInt(recommendations.length);
            final randomRec = recommendations[randomIndex];

            _exerciseName = randomRec['program_name'] ?? ""; 
            _placeName = randomRec['facility_name'] ?? "추천 장소";   
            _reason = randomRec['reason'] ?? "";
          } else {
            _exerciseName = "";
            _placeName = "주변 공원";
            _reason = "조건에 맞는 시설을 찾지 못했습니다.";
          }
          
          _isLoading = false;
        });
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
        actions: [
          TextButton(
            onPressed: () async {
              final shouldLogout = await showDialog<bool>(
                context: context,
                builder: (context) => AlertDialog(
                  title: const Text('로그아웃'),
                  content: const Text('로그아웃 하시겠습니까?'),
                  actions: [
                    TextButton(onPressed: () => Navigator.of(context).pop(false), child: const Text('취소')),
                    TextButton(onPressed: () => Navigator.of(context).pop(true), child: const Text('로그아웃')),
                  ],
                ),
              );

              if (shouldLogout == true) {
                Navigator.pushAndRemoveUntil(
                  context,
                  MaterialPageRoute(builder: (_) => const LoginScreen()),
                  (route) => false,
                );
              }
            },
            style: TextButton.styleFrom(foregroundColor: Colors.white),
            child: const Text('로그아웃', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
          ),
        ],
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

                // [수정] 부드러운 디자인의 집에서 운동하기 카드
                if (_homeExerciseData != null) ...[
                  Container(
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      color: Colors.orange.shade50, // 아주 연한 오렌지 배경 (경고 느낌 X)
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Row(
                          children: [
                            Icon(Icons.home, color: Colors.orange, size: 28),
                            SizedBox(width: 10),
                            Text("집에서 운동하기", style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Colors.black87)),
                          ],
                        ),
                        const SizedBox(height: 8),
                        const Text(
                          "간단한 실내 운동은 어떠세요?",
                          style: TextStyle(fontSize: 16, color: Colors.black54),
                        ),
                        const SizedBox(height: 16),
                        
                        // 운동 정보 간략 표시
                        Container(
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                _homeExerciseData!['name'],
                                style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                              ),
                              const SizedBox(height: 8),
                              // [수정] info 대신 체력항목, 운동도구 사용
                              Text("• 효과: ${_homeExerciseData!['체력항목']}", style: const TextStyle(fontSize: 15, color: Colors.black87)),
                              Text("• 도구: ${_homeExerciseData!['운동도구']}", style: const TextStyle(fontSize: 15, color: Colors.black87)),
                            ],
                          ),
                        ),
                        
                        const SizedBox(height: 16),
                        
                        SizedBox(
                          width: double.infinity,
                          child: ElevatedButton(
                            onPressed: () {
                              Navigator.push(
                                context,
                                MaterialPageRoute(
                                  builder: (context) => HomeExerciseScreen(
                                    exerciseName: _homeExerciseData!['name'],
                                    // 상세 화면에도 체력항목과 운동도구를 전달
                                    exerciseInfo: _homeExerciseData!['체력항목'] ?? "정보 없음",
                                    equipment: _homeExerciseData!['운동도구'] ?? "맨몸",
                                    videoUrl: _homeExerciseData!['url'],
                                  ),
                                ),
                              );
                            },
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.orange,
                              foregroundColor: Colors.white,
                              padding: const EdgeInsets.symmetric(vertical: 12),
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                            ),
                            child: const Text("영상 보러가기", style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 30),
                ],
                
                // 기존 시설 추천 카드
                Container(
                  padding: const EdgeInsets.all(24),
                  decoration: BoxDecoration(
                    color: primaryGreen,
                    borderRadius: BorderRadius.circular(24),
                  ),
                  child: Column(children: [
                    const Icon(Icons.directions_walk, size: 80, color: Colors.white),
                    const SizedBox(height: 20),

                    if (_exerciseName.isEmpty)
                      Text(
                        "오늘은 '$_placeName'에\n방문해보세요.",
                        style: const TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: Colors.white),
                        textAlign: TextAlign.center,
                      )
                    else ...[
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

                    ElevatedButton.icon(
                      onPressed: () {
                         Navigator.push(context, MaterialPageRoute(builder: (context) => MapScreen(
                           placeName: _placeName, 
                           latitude: _targetLat, 
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
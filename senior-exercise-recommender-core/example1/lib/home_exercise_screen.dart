import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

class HomeExerciseScreen extends StatelessWidget {
  final String exerciseName; // 운동 이름
  final String exerciseInfo; // 운동 정보 (효과 등)
  final String equipment;    // 필요 도구 (맨몸 등)
  final String videoUrl;     // 유튜브 링크

  const HomeExerciseScreen({
    super.key,
    required this.exerciseName,
    required this.exerciseInfo,
    required this.equipment,
    required this.videoUrl,
  });

  // 유튜브 링크 열기 함수
  Future<void> _launchURL() async {
    final Uri url = Uri.parse(videoUrl);
    if (!await launchUrl(url, mode: LaunchMode.externalApplication)) {
      throw Exception('Could not launch $url');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("집에서 운동하기"),
        backgroundColor: Colors.orange, // 실내 운동은 따뜻한 오렌지색
        foregroundColor: Colors.white,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // 1. 운동 제목
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Colors.orange.shade50,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: Colors.orange.shade200),
                ),
                child: Column(
                  children: [
                    const Icon(Icons.home_filled, size: 60, color: Colors.orange),
                    const SizedBox(height: 10),
                    const Text(
                      "오늘의 추천 홈트레이닝",
                      style: TextStyle(fontSize: 16, color: Colors.black54, fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 10),
                    Text(
                      exerciseName,
                      style: const TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: Colors.black87),
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 30),

              // 2. 운동 정보 (어디에 좋은지)
              _buildInfoCard("운동 효과 및 부위", exerciseInfo, Icons.accessibility_new),
              
              const SizedBox(height: 20),

              // 3. 필요 도구
              _buildInfoCard("필요한 도구", equipment, Icons.fitness_center),

              const SizedBox(height: 40),

              // 4. 유튜브 바로가기 버튼
              SizedBox(
                height: 60,
                child: ElevatedButton.icon(
                  onPressed: _launchURL,
                  icon: const Icon(Icons.play_circle_fill, size: 30, color: Colors.red),
                  label: const Text(
                    "운동 영상 보러가기 (YouTube)",
                    style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                  ),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.white,
                    foregroundColor: Colors.black87,
                    elevation: 3,
                    side: const BorderSide(color: Colors.red, width: 2),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  // 정보 카드 위젯 (코드 중복 방지)
  Widget _buildInfoCard(String title, String content, IconData icon) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(icon, color: Colors.orange, size: 24),
            const SizedBox(width: 8),
            Text(title, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
          ],
        ),
        const SizedBox(height: 10),
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: Colors.grey.shade300),
          ),
          child: Text(
            content,
            style: const TextStyle(fontSize: 18, height: 1.5),
          ),
        ),
      ],
    );
  }
}
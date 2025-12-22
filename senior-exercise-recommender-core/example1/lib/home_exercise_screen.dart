import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

class HomeExerciseScreen extends StatelessWidget {
  final String exerciseName;
  final String exerciseInfo; // 기본 정보 (체력항목 등)
  final String equipment;    // 운동 도구
  final String videoUrl;
  
  // [신규] LLM이 생성한 상세 정보들
  final List<String> reasons;   // 추천 이유
  final List<String> cautions;  // 주의사항
  final String nextStep;        // 다음 단계 제안

  const HomeExerciseScreen({
    super.key,
    required this.exerciseName,
    required this.exerciseInfo,
    required this.equipment,
    required this.videoUrl,
    required this.reasons,
    required this.cautions,
    required this.nextStep,
  });

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
        title: const Text("AI 맞춤 홈트레이닝"),
        backgroundColor: Colors.orange,
        foregroundColor: Colors.white,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // 1. 운동 제목 및 도구
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(16),
                  boxShadow: [
                    BoxShadow(color: Colors.orange.withOpacity(0.1), blurRadius: 10, offset: const Offset(0, 4))
                  ],
                  border: Border.all(color: Colors.orange.shade100),
                ),
                child: Column(
                  children: [
                    const Icon(Icons.self_improvement, size: 60, color: Colors.orange),
                    const SizedBox(height: 16),
                    Text(
                      exerciseName,
                      style: const TextStyle(fontSize: 26, fontWeight: FontWeight.bold, color: Colors.black87),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 10),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                      decoration: BoxDecoration(
                        color: Colors.grey.shade100,
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: Text(
                        "준비물: $equipment",
                        style: TextStyle(fontSize: 16, color: Colors.grey.shade700, fontWeight: FontWeight.w600),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 24),

              // 2. [LLM] 추천 이유 (왜 이 운동인가요?)
              if (reasons.isNotEmpty)
                _buildSection(
                  title: "이 운동을 추천하는 이유",
                  icon: Icons.thumb_up_alt_rounded,
                  color: Colors.blue,
                  content: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: reasons.map((r) => _buildBulletPoint(r)).toList(),
                  ),
                ),

              // 3. [LLM] 주의사항 (조심하세요!)
              if (cautions.isNotEmpty)
                _buildSection(
                  title: "주의하세요!",
                  icon: Icons.warning_rounded,
                  color: Colors.red,
                  content: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: cautions.map((c) => _buildBulletPoint(c)).toList(),
                  ),
                ),

              // 4. [LLM] 다음 단계 (발전하기)
              if (nextStep.isNotEmpty)
                _buildSection(
                  title: "더 나아가기",
                  icon: Icons.trending_up_rounded,
                  color: Colors.purple,
                  content: Text(
                    nextStep,
                    style: const TextStyle(fontSize: 16, height: 1.5, color: Colors.black87),
                  ),
                ),

              const SizedBox(height: 10),

              // 5. 유튜브 버튼
              SizedBox(
                height: 56,
                child: ElevatedButton.icon(
                  onPressed: _launchURL,
                  icon: const Icon(Icons.play_circle_fill, size: 28),
                  label: const Text("영상 보러가기", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.red, // 유튜브 색상
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    elevation: 4,
                  ),
                ),
              ),
              const SizedBox(height: 20),
            ],
          ),
        ),
      ),
    );
  }

  // 섹션 빌더 (카드 형태)
  Widget _buildSection({required String title, required IconData icon, required Color color, required Widget content}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 20.0),
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: color.withOpacity(0.05),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: color.withOpacity(0.2)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, color: color, size: 24),
                const SizedBox(width: 8),
                Text(title, style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: color)),
              ],
            ),
            const SizedBox(height: 12),
            content,
          ],
        ),
      ),
    );
  }

  // 리스트 아이템 빌더 (쩜 찍고 내용)
  Widget _buildBulletPoint(String text) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 6.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text("• ", style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
          Expanded(
            child: Text(text, style: const TextStyle(fontSize: 16, height: 1.4, color: Colors.black87)),
          ),
        ],
      ),
    );
  }
}
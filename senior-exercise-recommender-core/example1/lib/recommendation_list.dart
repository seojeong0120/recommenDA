import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'map_screen.dart';
import 'config.dart';

class RecommendationListScreen extends StatelessWidget {
  final List recommendations;
  final void Function(Map<String, dynamic>) onSelect;

  const RecommendationListScreen({super.key, required this.recommendations, required this.onSelect});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('추천 목록'),
        backgroundColor: Colors.teal,
      ),
      body: recommendations.isEmpty
          ? const Center(child: Text('추천 항목이 없습니다.'))
          : ListView.separated(
              padding: const EdgeInsets.all(12),
              itemCount: recommendations.length,
              separatorBuilder: (_, __) => const SizedBox(height: 8),
              itemBuilder: (context, idx) {
                final rec = recommendations[idx] as Map;
                final facility = rec['facility_name'] ?? '장소';
                final program = rec['program_name'] ?? '';
                final distance = (rec['distance_km'] != null) ? (rec['distance_km'] as num).toDouble() : null;

                return Card(
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  child: Padding(
                    padding: const EdgeInsets.all(12),
                    child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                      Text(facility, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                      const SizedBox(height: 6),
                      Text(program, style: const TextStyle(color: Colors.black54)),
                      const SizedBox(height: 6),
                      if (distance != null) Text('거리: ${distance.toStringAsFixed(2)} km', style: const TextStyle(color: Colors.black54)),
                      const SizedBox(height: 10),
                      Row(children: [
                        ElevatedButton(
                          onPressed: () {
                            Navigator.push(context, MaterialPageRoute(builder: (_) => MapScreen(
                              placeName: facility,
                              latitude: (rec['lat'] as num).toDouble(),
                              longitude: (rec['lon'] as num).toDouble(),
                            )));
                          },
                          child: const Text('지도 보기'),
                        ),
                        const SizedBox(width: 10),
                        OutlinedButton(
                          onPressed: () {
                            onSelect(Map<String, dynamic>.from(rec));
                            Navigator.pop(context);
                          },
                          child: const Text('선택'),
                        ),
                      ])
                    ]),
                  ),
                );
              },
            ),
    );
  }
}

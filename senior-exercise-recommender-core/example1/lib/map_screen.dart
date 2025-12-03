import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';

class MapScreen extends StatelessWidget {
  final String placeName;
  final double latitude;
  final double longitude;

  const MapScreen({
    super.key,
    required this.placeName,
    required this.latitude,
    required this.longitude,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(placeName),
        backgroundColor: Colors.teal,
        foregroundColor: Colors.white,
      ),
      body: FlutterMap(
        options: MapOptions(
          initialCenter: LatLng(latitude, longitude),
          initialZoom: 16.0,
        ),
        children: [
          TileLayer(
            urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
            // [수정] 여기에 본인의 진짜 패키지 이름을 넣어야 차단되지 않습니다!
            userAgentPackageName: 'com.example.example1', 
          ),
          MarkerLayer(
            markers: [
              Marker(
                point: LatLng(latitude, longitude),
                width: 80,
                height: 80,
                child: Column(
                  children: [
                    const Icon(
                      Icons.location_on,
                      color: Colors.red,
                      size: 40,
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(8),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withOpacity(0.2),
                            blurRadius: 6,
                          ),
                        ],
                      ),
                      child: const Text(
                        "여기!",
                        style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
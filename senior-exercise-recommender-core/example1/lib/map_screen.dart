import 'package:flutter/material.dart';
import 'package:flutter_naver_map/flutter_naver_map.dart';

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
    // 목표 지점 좌표 객체 생성
    final targetLocation = NLatLng(latitude, longitude);

    return Scaffold(
      appBar: AppBar(
        title: Text(placeName),
        backgroundColor: const Color(0xFF03C75A), // 네이버 시그니처 그린
        foregroundColor: Colors.white,
      ),
      body: NaverMap(
        options: NaverMapViewOptions(
          initialCameraPosition: NCameraPosition(
            target: targetLocation,
            zoom: 16, // 16 정도가 건물 보기 적당함
          ),
          mapType: NMapType.basic,
          // 건물, 대중교통 등 유용한 정보 표시
          activeLayerGroups: [
            NLayerGroup.building,
            NLayerGroup.transit,
          ],
        ),
        onMapReady: (controller) {
          // 1. 마커 생성
          final marker = NMarker(
            id: 'target_marker',
            position: targetLocation,
            caption: NOverlayCaption(text: placeName), // 마커 밑에 이름 표시
          );

          // 2. 정보창(말풍선) 생성
          final onMarkerInfoWindow = NInfoWindow.onMarker(
            id: marker.info.id,
            text: "$placeName\n여기서 운동하세요!",
          );

          // 3. 지도에 마커 추가 및 정보창 열기
          controller.addOverlay(marker);
          marker.openInfoWindow(onMarkerInfoWindow);
        },
      ),
    );
  }
}
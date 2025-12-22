import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'config.dart';

class MapScreen extends StatefulWidget {
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
  State<MapScreen> createState() => _MapScreenState();
}

class _MapScreenState extends State<MapScreen> {
  late MapController _mapController;
  String _roadAddress = "";

  @override
  void initState() {
    super.initState();
    _mapController = MapController();
    _fetchRoadAddress();
  }

  Future<void> _fetchRoadAddress() async {
    try {
      final Uri url = Uri.parse('$backendBaseUrl/api/reverse_geocode?lat=${widget.latitude}&lon=${widget.longitude}');
      final resp = await http.get(url).timeout(const Duration(seconds: 5));
      if (resp.statusCode == 200) {
        final Map data = jsonDecode(resp.body);
        final addr = data['address_road'];
        setState(() {
          _roadAddress = (addr != null && addr.toString().isNotEmpty) ? addr.toString() : '';
        });
      } else {
        print('역지오코드 서버 오류: ${resp.statusCode}');
      }
    } catch (e) {
      print('역지오코드 예외: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(widget.placeName),
            if (_roadAddress.isNotEmpty)
              Text(_roadAddress, style: const TextStyle(fontSize: 12))
            else
              Text('${widget.latitude.toStringAsFixed(5)}, ${widget.longitude.toStringAsFixed(5)}', style: const TextStyle(fontSize: 12)),
          ],
        ),
        backgroundColor: Colors.teal,
        foregroundColor: Colors.white,
      ),
      body: FlutterMap(
        mapController: _mapController,
        options: MapOptions(
          initialCenter: LatLng(widget.latitude, widget.longitude),
          initialZoom: 16.0,
        ),
        children: [
          TileLayer(
            urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
            userAgentPackageName: 'com.example.senior_exercise',
          ),
          MarkerLayer(
            markers: [
              Marker(
                point: LatLng(widget.latitude, widget.longitude),
                width: 56,
                height: 56,
                child: const Icon(Icons.location_on, color: Colors.red, size: 56),
              ),
            ],
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _mapController.dispose();
    super.dispose();
  }
}
import 'package:flutter_dotenv/flutter_dotenv.dart';

String get backendBaseUrl =>
    dotenv.env['BACKEND_BASE_URL'] ?? 'http://10.0.2.2:8000';
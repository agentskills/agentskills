import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;

class WordPressApi {
  WordPressApi(this.storage);

  final FlutterSecureStorage storage;
  static const apiRoot = 'https://public-api.wordpress.com/rest/v1.1';

  Future<List<dynamic>> posts() async {
    final token = await storage.read(key: 'access_token');
    if (token == null) throw StateError('Not signed in');
    final response = await http.get(
      Uri.parse('$apiRoot/sites/getachewnohe31-deujx.wordpress.com/posts/'),
      headers: {'Authorization': 'Bearer $token'},
    );
    if (response.statusCode != 200) {
      throw Exception('WordPress API error: ${response.statusCode}');
    }
    return (jsonDecode(response.body)['posts'] as List<dynamic>);
  }
}

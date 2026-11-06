import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'wordpress_api.dart';

void main() => runApp(const WordPressManagerApp());

class WordPressManagerApp extends StatelessWidget {
  const WordPressManagerApp({super.key});

  @override
  Widget build(BuildContext context) => MaterialApp(
        title: 'WordPress Manager',
        theme: ThemeData(colorSchemeSeed: Colors.blue, useMaterial3: true),
        home: const PostsPage(),
      );
}

class PostsPage extends StatefulWidget {
  const PostsPage({super.key});
  @override
  State<PostsPage> createState() => _PostsPageState();
}

class _PostsPageState extends State<PostsPage> {
  final api = WordPressApi(const FlutterSecureStorage());
  late Future<List<dynamic>> posts;

  @override
  void initState() {
    super.initState();
    posts = api.posts();
  }

  @override
  Widget build(BuildContext context) => Scaffold(
        appBar: AppBar(title: const Text('My WordPress Posts')),
        body: FutureBuilder<List<dynamic>>(
          future: posts,
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.waiting) {
              return const Center(child: CircularProgressIndicator());
            }
            if (snapshot.hasError) {
              return Center(child: Text('Sign in is not configured yet.\n${snapshot.error}'));
            }
            final items = snapshot.data!;
            return ListView.builder(
              itemCount: items.length,
              itemBuilder: (context, index) => ListTile(
                title: Text(items[index]['title'] ?? 'Untitled'),
                subtitle: Text(items[index]['date'] ?? ''),
              ),
            );
          },
        ),
      );
}

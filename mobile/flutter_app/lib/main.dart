import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;

const backendBaseUrl = String.fromEnvironment('BACKEND_BASE_URL', defaultValue: 'http://10.0.2.2:8000');

void main() {
  runApp(const AccountingApp());
}

class AccountingApp extends StatelessWidget {
  const AccountingApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Accounting',
      theme: ThemeData(primarySwatch: Colors.indigo),
      home: const LoginPage(),
    );
  }
}

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _storage = const FlutterSecureStorage();
  bool _loading = false;
  String? _error;

  Future<void> _login() async {
    setState(() { _loading = true; _error = null; });
    try {
      final response = await http.post(
        Uri.parse('$backendBaseUrl/api/v1/auth/login'),
        headers: { 'Content-Type': 'application/json' },
        body: jsonEncode({
          'email': _emailController.text,
          'password': _passwordController.text,
        }),
      );
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        final token = data['access_token'] as String?;
        if (token != null) {
          await _storage.write(key: 'access_token', value: token);
          if (!mounted) return;
          Navigator.of(context).pushReplacement(
            MaterialPageRoute(builder: (_) => const UsersPage()),
          );
        } else {
          setState(() { _error = 'Invalid token'; });
        }
      } else {
        setState(() { _error = 'Login failed (${response.statusCode})'; });
      }
    } catch (e) {
      setState(() { _error = 'Network error: $e'; });
    } finally {
      setState(() { _loading = false; });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Login')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            TextField(controller: _emailController, decoration: const InputDecoration(labelText: 'Email')),
            TextField(controller: _passwordController, decoration: const InputDecoration(labelText: 'Password'), obscureText: true),
            const SizedBox(height: 16),
            if (_error != null) Text(_error!, style: const TextStyle(color: Colors.red)),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _loading ? null : _login,
              child: _loading ? const CircularProgressIndicator() : const Text('Login'),
            ),
          ],
        ),
      ),
    );
  }
}

class UsersPage extends StatefulWidget {
  const UsersPage({super.key});

  @override
  State<UsersPage> createState() => _UsersPageState();
}

class _UsersPageState extends State<UsersPage> {
  final _storage = const FlutterSecureStorage();
  List<dynamic> _users = [];
  String? _error;

  Future<void> _loadUsers() async {
    setState(() { _error = null; });
    try {
      final token = await _storage.read(key: 'access_token');
      final response = await http.get(
        Uri.parse('$backendBaseUrl/api/v1/users/'),
        headers: token != null ? { 'Authorization': 'Bearer $token' } : {},
      );
      if (response.statusCode == 200) {
        setState(() { _users = jsonDecode(response.body) as List<dynamic>; });
      } else {
        setState(() { _error = 'Failed (${response.statusCode})'; });
      }
    } catch (e) {
      setState(() { _error = 'Network error: $e'; });
    }
  }

  @override
  void initState() {
    super.initState();
    _loadUsers();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Users')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: _error != null
          ? Text(_error!, style: const TextStyle(color: Colors.red))
          : ListView.builder(
              itemCount: _users.length,
              itemBuilder: (context, index) {
                final u = _users[index] as Map<String, dynamic>;
                return ListTile(
                  title: Text(u['email'] as String? ?? ''),
                  subtitle: Text((u['full_name'] as String?) ?? ''),
                );
              },
            ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _loadUsers,
        child: const Icon(Icons.refresh),
      ),
    );
  }
}

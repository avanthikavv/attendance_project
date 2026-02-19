import 'package:flutter/material.dart';
import 'package:attendance_app/api_service.dart';
import 'package:attendance_app/student_home.dart';
import 'package:attendance_app/teacher_home.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final emailController = TextEditingController();
  final passwordController = TextEditingController();

  bool isLoading = false;

  void login() async {
    setState(() {
      isLoading = true;
    });

    var response = await ApiService.login(
      emailController.text,
      passwordController.text,
    );

    print("LOGIN RESPONSE: $response");

    setState(() {
      isLoading = false;
    });

    if (response != null) {
      if (response["role"] == "student") {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (_) => StudentHome(studentId: response["student_id"]),
          ),
        );
      } else {
        Navigator.push(
          context,
          MaterialPageRoute(builder: (_) => const TeacherHome()),
        );
      }
    } else {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text("Login Failed")));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Login")),

      body: Padding(
        padding: const EdgeInsets.all(20),

        child: Column(
          children: [
            TextField(
              controller: emailController,
              decoration: const InputDecoration(labelText: "Email"),
            ),

            TextField(
              controller: passwordController,
              obscureText: true,
              decoration: const InputDecoration(labelText: "Password"),
            ),

            const SizedBox(height: 20),

            isLoading
                ? const CircularProgressIndicator()
                : ElevatedButton(onPressed: login, child: const Text("Login")),
          ],
        ),
      ),
    );
  }
}

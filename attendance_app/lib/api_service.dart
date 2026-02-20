import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  static const bool isProd = false; // true when final

  static const String baseUrl = isProd
      ? "https://attendance-project-gg16.onrender.com"
      : "http://10.0.2.2:5000";

  // ------------------------
  // Login
  // ------------------------
  static Future<Map<String, dynamic>?> login(
    String email,
    String password,
  ) async {
    try {
      var url = Uri.parse("$baseUrl/login");

      var response = await http.post(
        url,
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({"email": email, "password": password}),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      }

      return null;
    } catch (e) {
      print("LOGIN ERROR: $e");
      return null;
    }
  }

  // ------------------------
  // Check Attendance
  // ------------------------
  static Future<bool> checkAttendance(int studentId) async {
    try {
      var url = Uri.parse("$baseUrl/check_attendance/$studentId");

      var response = await http.get(url);

      if (response.statusCode == 200) {
        var data = jsonDecode(response.body);
        return data["marked"] == true;
      }

      return false;
    } catch (e) {
      print("Check Attendance Error: $e");
      return false;
    }
  }

  // ------------------------
  // Mark Attendance
  // ------------------------
  static Future<String> markAttendance(int studentId, String status) async {
    try {
      var url = Uri.parse("$baseUrl/mark_attendance");

      var response = await http.post(
        url,
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({"student_id": studentId, "status": status}),
      );

      if (response.statusCode == 200) {
        return "success";
      }

      if (response.statusCode == 409) {
        return "already_marked";
      }

      return "failed";
    } catch (e) {
      print("Attendance Error: $e");
      return "failed";
    }
  }

  // ------------------------
  // Create Session (Teacher)
  // ------------------------
  static Future<bool> createSession(
    int batchId,
    int courseId,
    int classroomId,
    String startTime,
    String endTime,
  ) async {
    try {
      var url = Uri.parse("$baseUrl/create_session");

      var response = await http.post(
        url,
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "batch_id": batchId,
          "course_id": courseId,
          "classroom_id": classroomId,
          "start_time": startTime,
          "end_time": endTime,
        }),
      );

      return response.statusCode == 200;
    } catch (e) {
      print("Create Session Error: $e");
      return false;
    }
  }

  // ------------------------
  // Get Active Session
  // ------------------------
  static Future<Map<String, dynamic>?> getActiveSession() async {
    try {
      var url = Uri.parse("$baseUrl/active_session");

      var response = await http.get(url);

      if (response.statusCode == 200) {
        var data = jsonDecode(response.body);

        if (data.containsKey("message")) {
          return null;
        }

        return data;
      }

      return null;
    } catch (e) {
      print("Active Session Error: $e");
      return null;
    }
  }

  // ------------------------
  // Student Dashboard Info
  // ------------------------
  static Future<Map<String, dynamic>?> getStudentDashboard(
    int studentId,
  ) async {
    try {
      var url = Uri.parse("$baseUrl/student_dashboard/$studentId");

      var response = await http.get(url);

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      }

      return null;
    } catch (e) {
      print("Dashboard Error: $e");
      return null;
    }
  }

  // ------------------------
  // Get Active Sessions (Student)
  // ------------------------
  static Future<List<dynamic>> getStudentActiveSessions(int studentId) async {
    try {
      var url = Uri.parse("$baseUrl/student_active_sessions/$studentId");

      var response = await http.get(url);

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      }

      return [];
    } catch (e) {
      print("Active Sessions Error: $e");
      return [];
    }
  }
}

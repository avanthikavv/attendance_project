import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  static const String baseUrl = "http://10.106.11.45:5000";

  static const Map<String, String> headers = {
    "Content-Type": "application/json",
  };

  // LOGIN
  static Future<Map<String, dynamic>?> login(
    String email,
    String password,
  ) async {
    try {
      var response = await http.post(
        Uri.parse("$baseUrl/login"),
        headers: headers,
        body: jsonEncode({
          "email": email,
          "password": password,
        }),
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

  // CHECK ATTENDANCE
  static Future<bool> checkAttendance(int studentId) async {
    try {
      var response = await http.get(
        Uri.parse("$baseUrl/check_attendance/$studentId"),
      );

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

  // MARK ATTENDANCE
  static Future<String> markAttendance(
    int studentId,
    String status,
  ) async {
    try {
      var response = await http.post(
        Uri.parse("$baseUrl/mark_attendance"),
        headers: headers,
        body: jsonEncode({
          "student_id": studentId,
          "status": status,
        }),
      );

      if (response.statusCode == 200) return "success";
      if (response.statusCode == 409) return "already_marked";

      return "failed";
    } catch (e) {
      print("Attendance Error: $e");
      return "failed";
    }
  }

  // CREATE SESSION
  static Future<bool> createSession(
    int batchId,
    int courseId,
    int classroomId,
    String startTime,
    String endTime,
  ) async {
    try {
      var response = await http.post(
        Uri.parse("$baseUrl/create_session"),
        headers: headers,
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

  // GET ACTIVE SESSION
  static Future<Map<String, dynamic>?> getActiveSession() async {
    try {
      var response = await http.get(
        Uri.parse("$baseUrl/active_session"),
      );

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

  // STUDENT DASHBOARD
  static Future<Map<String, dynamic>?> getStudentDashboard(
    int studentId,
  ) async {
    try {
      var response = await http.get(
        Uri.parse("$baseUrl/student_dashboard/$studentId"),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      }

      return null;
    } catch (e) {
      print("Dashboard Error: $e");
      return null;
    }
  }

  // STUDENT ACTIVE SESSIONS
  static Future<List<dynamic>> getStudentActiveSessions(
    int studentId,
  ) async {
    try {
      var response = await http.get(
        Uri.parse("$baseUrl/student_active_sessions/$studentId"),
      );

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

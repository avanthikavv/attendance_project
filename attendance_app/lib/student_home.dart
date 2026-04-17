import 'package:flutter/material.dart';
import 'api_service.dart';
import 'package:local_auth/local_auth.dart';

class StudentHome extends StatefulWidget {
  final int studentId;

  const StudentHome({super.key, required this.studentId});

  @override
  State<StudentHome> createState() => _StudentHomeState();
}

class _StudentHomeState extends State<StudentHome> {
  final LocalAuthentication auth = LocalAuthentication();

  bool isLoading = true;

  List sessions = [];

  @override
  void initState() {
    super.initState();
    loadSessions();
  }

  void loadSessions() async {
    var data = await ApiService.getStudentActiveSessions(
      widget.studentId,
    );

    setState(() {
      sessions = data;
      isLoading = false;
    });
  }

  void markAttendance(int sessionId) async {
    bool verified = await authenticateUser();

    if (!verified) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Biometric Verification Failed ❌")),
      );
      return;
    }

    setState(() => isLoading = true);

    String result = await ApiService.markAttendance(
      widget.studentId,
      "Present",
    );

    setState(() => isLoading = false);

    if (result == "success") {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Attendance Marked Successfully ✅")),
      );
    } else if (result == "already_marked") {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Already Marked ⚠️")),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Attendance Failed ❌")),
      );
    }

    loadSessions();
  }

  Widget sessionCard(Map data) {
    bool marked = data["already_marked"] == 1;

    return Container(
      margin: const EdgeInsets.symmetric(vertical: 10),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(18),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.4),
            blurRadius: 12,
            offset: const Offset(0, 6),
          )
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.menu_book, color: Colors.blueAccent),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  data["course_name"],
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              const Icon(Icons.location_on, size: 18, color: Colors.grey),
              const SizedBox(width: 5),
              Text(
                data["room_name"],
                style: const TextStyle(color: Colors.grey),
              ),
            ],
          ),
          const SizedBox(height: 18),
          marked
              ? Container(
                  width: double.infinity,
                  padding: const EdgeInsets.symmetric(vertical: 10),
                  decoration: BoxDecoration(
                    color: Colors.green.withOpacity(0.15),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: const Center(
                    child: Text(
                      "✔ Attendance Marked",
                      style: TextStyle(
                        color: Colors.green,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                )
              : SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    onPressed: () {
                      markAttendance(data["session_id"]);
                    },
                    icon: const Icon(Icons.fingerprint),
                    label: const Text("Mark Attendance"),
                  ),
                ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Student Dashboard"),
        centerTitle: true,
        backgroundColor: Colors.transparent,
        elevation: 0,
      ),
      body: isLoading
          ? const Center(
              child: CircularProgressIndicator(strokeWidth: 3),
            )
          : sessions.isEmpty
              ? const Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.event_busy, size: 60, color: Colors.grey),
                      SizedBox(height: 10),
                      Text(
                        "No Active Sessions",
                        style: TextStyle(fontSize: 18, color: Colors.grey),
                      ),
                    ],
                  ),
                )
              : Padding(
                  padding: const EdgeInsets.all(20),
                  child: ListView.builder(
                    itemCount: sessions.length,
                    itemBuilder: (context, index) {
                      return sessionCard(sessions[index]);
                    },
                  ),
                ),
    );
  }

  Future<bool> authenticateUser() async {
    try {
      bool canCheck = await auth.canCheckBiometrics;

      if (!canCheck) {
        return false;
      }

      bool authenticated = await auth.authenticate(
        localizedReason: 'Verify to mark attendance',
        options: const AuthenticationOptions(
          biometricOnly: true,
          useErrorDialogs: true,
          stickyAuth: true,
        ),
      );

      return authenticated;
    } catch (e) {
      return false;
    }
  }
}

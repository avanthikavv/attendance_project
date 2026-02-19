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

  // ------------------------
  // Load Sessions
  // ------------------------
  void loadSessions() async {
    var data = await ApiService.getStudentActiveSessions(
      widget.studentId,
    );

    setState(() {
      sessions = data;
      isLoading = false;
    });
  }

  // ------------------------
  // Mark Attendance
  // ------------------------
  // ------------------------
// Mark Attendance
// ------------------------
  void markAttendance(int sessionId) async {
    print("MARK BUTTON PRESSED");

    // Step 1: Biometric Check
    bool verified = await authenticateUser();

    if (!verified) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text("Biometric Verification Failed ❌"),
        ),
      );
      return;
    }

    // Step 2: If biometric success → Call backend
    setState(() {
      isLoading = true;
    });

    String result = await ApiService.markAttendance(
      widget.studentId,
      "Present",
    );

    setState(() {
      isLoading = false;
    });

    if (result == "success") {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text("Attendance Marked Successfully ✅"),
        ),
      );
    } else if (result == "already_marked") {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text("Already Marked ⚠️"),
        ),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text("Attendance Failed ❌"),
        ),
      );
    }

    loadSessions();
  }

  // ------------------------
  // Session Card
  // ------------------------
  Widget sessionCard(Map data) {
    bool marked = data["already_marked"] == 1;

    return Container(
      margin: const EdgeInsets.symmetric(vertical: 8),
      padding: const EdgeInsets.all(15),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: Colors.grey),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            "Course: ${data["course_name"]}",
            style: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 5),
          Text("Classroom: ${data["room_name"]}"),
          const SizedBox(height: 15),
          Center(
            child: marked
                ? const Text(
                    "Already Marked ✅",
                    style: TextStyle(
                      color: Colors.green,
                      fontWeight: FontWeight.bold,
                    ),
                  )
                : ElevatedButton(
                    onPressed: () {
                      markAttendance(
                        data["session_id"],
                      );
                    },
                    child: const Text("Mark Attendance"),
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
      ),
      body: isLoading
          ? const Center(
              child: CircularProgressIndicator(),
            )
          : sessions.isEmpty
              ? const Center(
                  child: Text(
                    "No Active Sessions ❌",
                    style: TextStyle(fontSize: 18),
                  ),
                )
              : Padding(
                  padding: const EdgeInsets.all(20),
                  child: ListView.builder(
                    itemCount: sessions.length,
                    itemBuilder: (context, index) {
                      return sessionCard(
                        sessions[index],
                      );
                    },
                  ),
                ),
    );
  }

// ------------------------
// Biometric Verification
// ------------------------
  Future<bool> authenticateUser() async {
    try {
      print("BIOMETRIC FUNCTION STARTED");

      // Check if device supports biometrics
      bool isAvailable = await auth.isDeviceSupported();

      if (!isAvailable) {
        print("Biometric not supported");
        return false;
      }

      // Check if biometrics are enrolled
      bool canCheck = await auth.canCheckBiometrics;

      if (!canCheck) {
        print("No biometrics enrolled");
        return false;
      }

      // Authenticate
      bool authenticated = await auth.authenticate(
        localizedReason: 'Verify to mark attendance',
        options: const AuthenticationOptions(
          biometricOnly: true,
          useErrorDialogs: true,
          stickyAuth: true,
        ),
      );

      print("Biometric result: $authenticated");

      return authenticated;
    } catch (e) {
      print("Biometric Error: $e");
      return false;
    }
  }
}

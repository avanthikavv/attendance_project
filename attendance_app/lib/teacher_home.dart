import 'package:flutter/material.dart';
import 'api_service.dart';

class TeacherHome extends StatefulWidget {
  const TeacherHome({super.key});

  @override
  State<TeacherHome> createState() => _TeacherHomeState();
}

class _TeacherHomeState extends State<TeacherHome> {
  final batchIdController = TextEditingController();
  final courseIdController = TextEditingController();
  final classroomIdController = TextEditingController();

  DateTime? selectedDate;
  TimeOfDay? startTime;
  TimeOfDay? endTime;

  bool isLoading = false;

  // -------------------------
  // Pick Date
  // -------------------------
  Future<void> pickDate() async {
    DateTime? date = await showDatePicker(
      context: context,
      initialDate: DateTime.now(),
      firstDate: DateTime(2025),
      lastDate: DateTime(2030),
    );

    if (date != null) {
      setState(() {
        selectedDate = date;
      });
    }
  }

  // -------------------------
  // Pick Start Time (24H)
  // -------------------------
  Future<void> pickStartTime() async {
    TimeOfDay? time = await showTimePicker(
      context: context,
      initialTime: TimeOfDay.now(),
      builder: (context, child) {
        return MediaQuery(
          data: MediaQuery.of(context).copyWith(alwaysUse24HourFormat: true),
          child: child!,
        );
      },
    );

    if (time != null) {
      setState(() {
        startTime = time;
      });
    }
  }

  // -------------------------
  // Pick End Time (24H)
  // -------------------------
  Future<void> pickEndTime() async {
    TimeOfDay? time = await showTimePicker(
      context: context,
      initialTime: TimeOfDay.now(),
      builder: (context, child) {
        return MediaQuery(
          data: MediaQuery.of(context).copyWith(alwaysUse24HourFormat: true),
          child: child!,
        );
      },
    );

    if (time != null) {
      setState(() {
        endTime = time;
      });
    }
  }

  // -------------------------
  // Format Date + Time
  // -------------------------
  String formatDateTime(DateTime date, TimeOfDay time) {
    final dt = DateTime(
      date.year,
      date.month,
      date.day,
      time.hour,
      time.minute,
    );

    return dt.toString().substring(0, 19);
  }

  // -------------------------
  // Create Session
  // -------------------------
  void createSession() async {
    if (selectedDate == null || startTime == null || endTime == null) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text("Select date & time")));

      return;
    }

    String start = formatDateTime(selectedDate!, startTime!);
    String end = formatDateTime(selectedDate!, endTime!);

    setState(() {
      isLoading = true;
    });

    bool success = await ApiService.createSession(
      int.parse(batchIdController.text),
      int.parse(courseIdController.text),
      int.parse(classroomIdController.text),

      start,
      end,
    );

    setState(() {
      isLoading = false;
    });

    if (success) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text("Session Created ✅")));
    } else {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text("Session Failed ❌")));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Teacher Dashboard")),

      body: Padding(
        padding: const EdgeInsets.all(20),

        child: SingleChildScrollView(
          child: Column(
            children: [
              const Text(
                "Create Attendance Session",
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),

              const SizedBox(height: 20),

              TextField(
                controller: batchIdController,
                decoration: const InputDecoration(labelText: "Batch ID"),
              ),

              TextField(
                controller: courseIdController,
                decoration: const InputDecoration(labelText: "Course ID"),
              ),

              TextField(
                controller: classroomIdController,
                decoration: const InputDecoration(labelText: "Classroom ID"),
              ),

              const SizedBox(height: 20),

              ElevatedButton(
                onPressed: pickDate,
                child: Text(
                  selectedDate == null
                      ? "Select Date"
                      : "Date: ${selectedDate!.toLocal()}".split(' ')[0],
                ),
              ),

              ElevatedButton(
                onPressed: pickStartTime,
                child: Text(
                  startTime == null
                      ? "Select Start Time"
                      : "Start: ${startTime!.format(context)}",
                ),
              ),

              ElevatedButton(
                onPressed: pickEndTime,
                child: Text(
                  endTime == null
                      ? "Select End Time"
                      : "End: ${endTime!.format(context)}",
                ),
              ),

              const SizedBox(height: 30),

              isLoading
                  ? const CircularProgressIndicator()
                  : ElevatedButton(
                      onPressed: createSession,
                      child: const Text("Create Session"),
                    ),
            ],
          ),
        ),
      ),
    );
  }
}

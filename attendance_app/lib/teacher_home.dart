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

  Future<void> pickDate() async {
    DateTime? date = await showDatePicker(
      context: context,
      initialDate: DateTime.now(),
      firstDate: DateTime(2025),
      lastDate: DateTime(2030),
    );

    if (date != null) {
      setState(() => selectedDate = date);
    }
  }

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
      setState(() => startTime = time);
    }
  }

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
      setState(() => endTime = time);
    }
  }

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

  void createSession() async {
    if (selectedDate == null || startTime == null || endTime == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Select date & time")),
      );
      return;
    }

    String start = formatDateTime(selectedDate!, startTime!);
    String end = formatDateTime(selectedDate!, endTime!);

    setState(() => isLoading = true);

    bool success = await ApiService.createSession(
      int.parse(batchIdController.text),
      int.parse(courseIdController.text),
      int.parse(classroomIdController.text),
      start,
      end,
    );

    setState(() => isLoading = false);

    if (success) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Session Created ✅")),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Session Failed ❌")),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Teacher Dashboard"),
        centerTitle: true,
        backgroundColor: Colors.transparent,
        elevation: 0,
      ),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: SingleChildScrollView(
          child: Column(
            children: [
              const SizedBox(height: 10),
              const Icon(
                Icons.dashboard_customize,
                size: 60,
                color: Colors.blueAccent,
              ),
              const SizedBox(height: 10),
              const Text(
                "Create Attendance Session",
                style: TextStyle(
                  fontSize: 22,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 25),
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: const Color(0xFF1E293B),
                  borderRadius: BorderRadius.circular(20),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.4),
                      blurRadius: 12,
                      offset: const Offset(0, 6),
                    )
                  ],
                ),
                child: Column(
                  children: [
                    TextField(
                      controller: batchIdController,
                      decoration: const InputDecoration(
                        labelText: "Batch ID",
                        prefixIcon: Icon(Icons.group),
                      ),
                    ),
                    const SizedBox(height: 15),
                    TextField(
                      controller: courseIdController,
                      decoration: const InputDecoration(
                        labelText: "Course ID",
                        prefixIcon: Icon(Icons.book),
                      ),
                    ),
                    const SizedBox(height: 15),
                    TextField(
                      controller: classroomIdController,
                      decoration: const InputDecoration(
                        labelText: "Classroom ID",
                        prefixIcon: Icon(Icons.meeting_room),
                      ),
                    ),
                    const SizedBox(height: 25),
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton.icon(
                        onPressed: pickDate,
                        icon: const Icon(Icons.calendar_today),
                        label: Text(
                          selectedDate == null
                              ? "Select Date"
                              : "${selectedDate!.toLocal()}".split(' ')[0],
                        ),
                      ),
                    ),
                    const SizedBox(height: 10),
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton.icon(
                        onPressed: pickStartTime,
                        icon: const Icon(Icons.access_time),
                        label: Text(
                          startTime == null
                              ? "Start Time"
                              : "${startTime!.format(context)}",
                        ),
                      ),
                    ),
                    const SizedBox(height: 10),
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton.icon(
                        onPressed: pickEndTime,
                        icon: const Icon(Icons.access_time_filled),
                        label: Text(
                          endTime == null
                              ? "End Time"
                              : "${endTime!.format(context)}",
                        ),
                      ),
                    ),
                    const SizedBox(height: 30),
                    isLoading
                        ? const CircularProgressIndicator()
                        : SizedBox(
                            width: double.infinity,
                            child: ElevatedButton(
                              onPressed: createSession,
                              child: const Text("CREATE SESSION"),
                            ),
                          ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

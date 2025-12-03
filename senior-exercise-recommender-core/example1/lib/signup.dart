import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'user_location.dart';

class SignUpPage extends StatefulWidget {
  const SignUpPage({super.key, required this.title});
  final String title;

  @override
  State<SignUpPage> createState() => _SignUpPageState();
}

class _SignUpPageState extends State<SignUpPage> {
<<<<<<< HEAD
  // 컨트롤러
=======
  // 컨트롤러 추가 (ID, PW)
>>>>>>> 6f0b9ce7f2b49bf894db922eed57eccd4949f933
  final TextEditingController _idController = TextEditingController();
  final TextEditingController _pwController = TextEditingController();
  final TextEditingController _nameController = TextEditingController();
  final TextEditingController _birthController = TextEditingController();
  final TextEditingController _phoneController = TextEditingController(); // 연락처용
  final TextEditingController _guardianPhoneController = TextEditingController();

  String? _selectedGender;
  final List<String> _selectedHealthIssues = [];
  final List<String> _healthOptions = ["무릎 통증", "고혈압", "허리 통증", "관절염", "해당 없음"];
  final List<String> _selectedGoals = [];
  final List<String> _goalOptions = ["혈압 조절", "체중 감량", "건강 증진", "유연성 강화", "사회 활동"];
  String? _selectedPreference;

  bool _isButtonActive = false;

  bool _isValidDate(String input) {
    if (input.length != 6) return false;
    int month = int.tryParse(input.substring(2, 4)) ?? 0;
    int day = int.tryParse(input.substring(4, 6)) ?? 0;
    if (month < 1 || month > 12) return false;
    if (day < 1 || day > 31) return false;
    return true;
  }

  void _checkFormValidity() {
<<<<<<< HEAD
    bool isIdValid = _idController.text.isNotEmpty;
    bool isPwValid = _pwController.text.length >= 4;
=======
    // 유효성 검사 항목 추가 (ID, PW)
    bool isIdValid = _idController.text.isNotEmpty;
    bool isPwValid = _pwController.text.length >= 4; // 최소 4자리
>>>>>>> 6f0b9ce7f2b49bf894db922eed57eccd4949f933
    bool isNameValid = _nameController.text.isNotEmpty;
    bool isBirthValid = _isValidDate(_birthController.text);
    bool isGenderValid = _selectedGender != null;
    bool isPlaceValid = _selectedPreference != null;
    
<<<<<<< HEAD
    // 전화번호는 선택 사항 또는 필수 사항 여부에 따라 조정 가능
    // 여기서는 간단히 체크
    bool isPhoneValid = true; 

    bool isValid = isIdValid && isPwValid && isNameValid && isBirthValid && isGenderValid && isPlaceValid && isPhoneValid;
=======
    // 건강 상태와 목적은 필수 아님 (선택사항)
    // bool isHealthSelected = _selectedHealthIssues.isNotEmpty; 
    // bool isGoalSelected = _selectedGoals.isNotEmpty;

    RegExp phoneRegex = RegExp(r'^010-\d{4}-\d{4}$');
    bool isPhoneValid = phoneRegex.hasMatch(_phoneController.text);
    bool isGuardianPhoneValid = phoneRegex.hasMatch(_guardianPhoneController.text);

    bool isValid = isIdValid && isPwValid && isNameValid && isBirthValid && isGenderValid && 
                   isPlaceValid && isPhoneValid && isGuardianPhoneValid;
>>>>>>> 6f0b9ce7f2b49bf894db922eed57eccd4949f933

    if (isValid != _isButtonActive) {
      setState(() { _isButtonActive = isValid; });
    }
  }

  void _toggleMultiSelect(List<String> list, String value) {
    setState(() {
      if (value == "해당 없음") {
        list.clear();
        list.add(value);
      } else {
        if (list.contains("해당 없음")) list.remove("해당 없음");
        if (list.contains(value)) {
          list.remove(value);
        } else {
          list.add(value);
        }
      }
      _checkFormValidity();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(widget.title, style: const TextStyle(fontWeight: FontWeight.bold))),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
<<<<<<< HEAD
              const Text("회원가입 정보 입력", style: TextStyle(fontSize: 26, fontWeight: FontWeight.bold, color: Color(0xFF1B5E20))),
              const SizedBox(height: 30),

              // [신규] 아이디 (이 값이 api.py의 phone 필드로 들어갑니다)
              _buildLabel("아이디 (로그인용)"),
=======
              const Text("회원가입을 위해\n정보를 입력해주세요.", style: TextStyle(fontSize: 26, fontWeight: FontWeight.bold, color: Color(0xFF1B5E20))),
              const SizedBox(height: 30),

              // [신규] 아이디
              _buildLabel("아이디"),
>>>>>>> 6f0b9ce7f2b49bf894db922eed57eccd4949f933
              _buildTextField(controller: _idController, hint: "아이디 입력", inputType: TextInputType.text),
              const SizedBox(height: 24),

              // [신규] 비밀번호
              _buildLabel("비밀번호"),
              TextField(
                controller: _pwController,
                obscureText: true,
                onChanged: (v) => _checkFormValidity(),
                style: const TextStyle(fontSize: 22),
                decoration: InputDecoration(
                  hintText: "비밀번호 입력",
                  hintStyle: TextStyle(color: Colors.grey[500], fontSize: 18),
                  filled: true,
                  fillColor: Colors.white,
                  contentPadding: const EdgeInsets.symmetric(vertical: 16, horizontal: 16),
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                ),
              ),
              const SizedBox(height: 24),

              _buildLabel("이름"),
              _buildTextField(controller: _nameController, hint: "이름 입력", inputType: TextInputType.text),
              const SizedBox(height: 24),

              _buildLabel("생년월일 (6자리)"),
              _buildTextField(controller: _birthController, hint: "예: 540319", inputType: TextInputType.number, maxLength: 6),
              const SizedBox(height: 24),

              _buildLabel("성별"),
              Row(children: [
                Expanded(child: _buildSingleSelectButton("남성", _selectedGender, (v) => setState((){ _selectedGender = v; _checkFormValidity(); }))),
                const SizedBox(width: 8),
                Expanded(child: _buildSingleSelectButton("여성", _selectedGender, (v) => setState((){ _selectedGender = v; _checkFormValidity(); }))),
              ]),
              const SizedBox(height: 24),

              _buildLabel("건강 상태 (중복 선택 가능)"),
              Wrap(spacing: 8.0, runSpacing: 8.0, children: _healthOptions.map((o) => _buildMultiSelectChip(o, _selectedHealthIssues)).toList()),
              const SizedBox(height: 24),

              _buildLabel("운동 목적 (중복 선택 가능)"),
              Wrap(spacing: 8.0, runSpacing: 8.0, children: _goalOptions.map((o) => _buildMultiSelectChip(o, _selectedGoals)).toList()),
              const SizedBox(height: 24),

              _buildLabel("선호하는 장소"),
              Row(children: [
                Expanded(child: _buildSingleSelectButton("실내", _selectedPreference, (v) => setState((){ _selectedPreference = v; _checkFormValidity(); }))),
                const SizedBox(width: 8),
                Expanded(child: _buildSingleSelectButton("실외", _selectedPreference, (v) => setState((){ _selectedPreference = v; _checkFormValidity(); }))),
                const SizedBox(width: 8),
                Expanded(child: _buildSingleSelectButton("둘 다", _selectedPreference, (v) => setState((){ _selectedPreference = v; _checkFormValidity(); }))),
              ]),
              const SizedBox(height: 24),

              _buildLabel("연락처 (선택)"),
              _buildTextField(controller: _phoneController, hint: "010-0000-0000", inputType: TextInputType.phone),
              const SizedBox(height: 50),

              SizedBox(
                width: double.infinity,
                height: 60,
                child: ElevatedButton(
                  onPressed: _isButtonActive ? () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => UserLocationScreen(
<<<<<<< HEAD
                          userId: _idController.text, // 입력받은 아이디 전달
                          password: _pwController.text, // 입력받은 비번 전달
=======
                          userId: _idController.text, // ID 전달
                          password: _pwController.text, // PW 전달
>>>>>>> 6f0b9ce7f2b49bf894db922eed57eccd4949f933
                          name: _nameController.text,
                          birthdate: _birthController.text,
                          gender: _selectedGender!,
                          healthIssues: _selectedHealthIssues,
                          goals: _selectedGoals,
                          preference: _selectedPreference!,
                        ),
                      ),
                    );
                  } : null,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: _isButtonActive ? const Color(0xFF2E7D32) : Colors.grey[400],
                    foregroundColor: Colors.white,
                    textStyle: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                  child: const Text('다음 단계로'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildLabel(String text) => Padding(padding: const EdgeInsets.only(bottom: 8.0), child: Text(text, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Color(0xFF1B5E20))));

  Widget _buildTextField({required TextEditingController controller, required String hint, required TextInputType inputType, int? maxLength}) {
    return TextField(
      controller: controller, keyboardType: inputType, maxLength: maxLength,
      style: const TextStyle(fontSize: 22),
      onChanged: (v) => _checkFormValidity(),
      decoration: InputDecoration(
        hintText: hint, counterText: "", filled: true, fillColor: Colors.white,
        contentPadding: const EdgeInsets.symmetric(vertical: 16, horizontal: 16),
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
      ),
    );
  }

  Widget _buildSingleSelectButton(String value, String? groupValue, Function(String) onTap) {
    bool isSelected = groupValue == value;
    return GestureDetector(
      onTap: () => onTap(value),
      child: Container(
        height: 55, alignment: Alignment.center,
        decoration: BoxDecoration(
          color: isSelected ? const Color(0xFF2E7D32) : Colors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: isSelected ? const Color(0xFF2E7D32) : Colors.grey[400]!, width: isSelected ? 2.0 : 1.0),
        ),
        child: Text(value, style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: isSelected ? Colors.white : Colors.grey[600])),
      ),
    );
  }

  Widget _buildMultiSelectChip(String label, List<String> selectedList) {
    bool isSelected = selectedList.contains(label);
    return GestureDetector(
      onTap: () => _toggleMultiSelect(selectedList, label),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: isSelected ? const Color(0xFF2E7D32) : Colors.white,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: isSelected ? const Color(0xFF2E7D32) : Colors.grey[400]!, width: 1.5),
        ),
        child: Text(
          label,
          style: TextStyle(
            fontSize: 18, 
            fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
            color: isSelected ? Colors.white : Colors.black87
          ),
        ),
      ),
    );
  }
}
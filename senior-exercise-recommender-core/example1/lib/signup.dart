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
  final TextEditingController _nameController = TextEditingController();
  final TextEditingController _birthController = TextEditingController();
  final TextEditingController _phoneController = TextEditingController();
  final TextEditingController _guardianPhoneController = TextEditingController();

  // 1. 성별 (단일 선택)
  String? _selectedGender;

  // 2. 건강 상태 (복수 선택 가능)
  final List<String> _selectedHealthIssues = [];
  final List<String> _healthOptions = ["무릎 통증", "고혈압", "허리 통증", "관절염", "해당 없음"];

  // 3. 운동 목적 (복수 선택 가능)
  final List<String> _selectedGoals = [];
  final List<String> _goalOptions = ["혈압 조절", "체중 감량", "건강 증진", "유연성 강화", "사회 활동"];

  // [추가됨] 4. 선호하는 장소 (단일 선택)
  String? _selectedPreference; // "실내", "실외", "둘 다"

  bool _isButtonActive = false;

  // 날짜 유효성 검사
  bool _isValidDate(String input) {
    if (input.length != 6) return false;
    int month = int.tryParse(input.substring(2, 4)) ?? 0;
    int day = int.tryParse(input.substring(4, 6)) ?? 0;
    if (month < 1 || month > 12) return false;
    if (day < 1 || day > 31) return false;
    return true;
  }

  // 유효성 검사 (필수 항목 체크)
  void _checkFormValidity() {
    bool isNameValid = _nameController.text.isNotEmpty;
    bool isBirthValid = _isValidDate(_birthController.text);
    bool isGenderValid = _selectedGender != null;
    
    // [추가됨] 장소 선택 여부 확인
    bool isPlaceValid = _selectedPreference != null;
    
    // 건강 상태와 목적은 하나 이상 선택해야 한다고 가정 (필수가 아니라면 이 줄 제거 가능)
    bool isHealthSelected = _selectedHealthIssues.isNotEmpty; 
    bool isGoalSelected = _selectedGoals.isNotEmpty;

    RegExp phoneRegex = RegExp(r'^010-\d{4}-\d{4}$');
    bool isPhoneValid = phoneRegex.hasMatch(_phoneController.text);
    bool isGuardianPhoneValid = phoneRegex.hasMatch(_guardianPhoneController.text);

    bool isValid = isNameValid && isBirthValid && isGenderValid && 
                   isPlaceValid && isHealthSelected && isGoalSelected &&
                   isPhoneValid && isGuardianPhoneValid;

    if (isValid != _isButtonActive) {
      setState(() { _isButtonActive = isValid; });
    }
  }

  // 복수 선택 토글 로직
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
              const Text("맞춤 운동 추천을 위해\n상세 정보를 알려주세요.", style: TextStyle(fontSize: 26, fontWeight: FontWeight.bold, color: Color(0xFF1B5E20))),
              const SizedBox(height: 30),

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

              // 건강 상태 (복수 선택 - Wrap 사용)
              _buildLabel("건강 상태 (중복 선택 가능)"),
              Wrap(
                spacing: 8.0, 
                runSpacing: 8.0,
                children: _healthOptions.map((option) {
                  return _buildMultiSelectChip(option, _selectedHealthIssues);
                }).toList(),
              ),
              const SizedBox(height: 24),

              // 운동 목적 (복수 선택 - Wrap 사용)
              _buildLabel("운동 목적 (중복 선택 가능)"),
              Wrap(
                spacing: 8.0,
                runSpacing: 8.0,
                children: _goalOptions.map((option) {
                  return _buildMultiSelectChip(option, _selectedGoals);
                }).toList(),
              ),
              const SizedBox(height: 24),

              // [추가됨] 선호하는 장소 (단일 선택)
              _buildLabel("선호하는 장소"),
              Row(children: [
                Expanded(child: _buildSingleSelectButton("실내", _selectedPreference, (v) => setState((){ _selectedPreference = v; _checkFormValidity(); }))),
                const SizedBox(width: 8),
                Expanded(child: _buildSingleSelectButton("실외", _selectedPreference, (v) => setState((){ _selectedPreference = v; _checkFormValidity(); }))),
                const SizedBox(width: 8),
                Expanded(child: _buildSingleSelectButton("둘 다", _selectedPreference, (v) => setState((){ _selectedPreference = v; _checkFormValidity(); }))),
              ]),
              const SizedBox(height: 24),

              _buildLabel("전화번호"),
              _buildTextField(controller: _phoneController, hint: "010-0000-0000", inputType: TextInputType.phone),
              const SizedBox(height: 24),

              _buildLabel("보호자 전화번호"),
              _buildTextField(controller: _guardianPhoneController, hint: "010-0000-0000", inputType: TextInputType.phone),
              const SizedBox(height: 50),

              SizedBox(
                width: double.infinity,
                height: 60,
                child: ElevatedButton(
                  onPressed: _isButtonActive ? () {
                    // 다음 화면으로 데이터 전달 (장소 선호도 포함)
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => UserLocationScreen(
                          name: _nameController.text,
                          birthdate: _birthController.text,
                          gender: _selectedGender!,
                          healthIssues: _selectedHealthIssues, // 리스트 전달
                          goals: _selectedGoals,               // 리스트 전달
                          preference: _selectedPreference!,    // [추가됨] 장소 선호도 전달
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
                  child: const Text('정보 입력 완료'),
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

  // 단일 선택 버튼 (성별, 장소)
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

  // 복수 선택 칩 (건강, 목적)
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
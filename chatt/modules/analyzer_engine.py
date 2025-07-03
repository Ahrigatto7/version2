# 파일 경로: modules/analyzer_engine.py

from korean_lunar_calendar import KoreanLunarCalendar
from datetime import datetime, time
from typing import Dict

# 천간과 지지 리스트 (계산에 필요)
CHEONGAN = "갑을병정무기경신임계"
JIJI = "자축인묘진사오미신유술해"
JIJI_TIMES = [time(23, 30), time(1, 30), time(3, 30), time(5, 30), time(7, 30), time(9, 30), time(11, 30),
              time(13, 30), time(15, 30), time(17, 30), time(19, 30), time(21, 30)]

def get_ganji(year, month, day, hour):
    """ 양력 날짜를 기반으로 간지를 계산하는 함수 """
    # 년주 계산
    year_gan = CHEONGAN[(year - 4) % 10]
    year_ji = JIJI[(year - 4) % 12]
    
    # 월주 계산 (절기 기준, 여기서는 단순화된 로직 사용)
    # 실제로는 월별 절입 시간을 기준으로 복잡한 계산이 필요합니다.
    month_gan = CHEONGAN[((year - 1900) * 12 + month + 1) % 10]
    month_ji = JIJI[(month + 1) % 12]

    # 일주 계산 (라이브러리 사용)
    calendar = KoreanLunarCalendar()
    calendar.setSolarDate(year, month, day)
    ilju = calendar.getGanjiString()
    day_gan = ilju[0]
    day_ji = ilju[1]

    # 시주 계산
    # 일간에 따른 시간별 천간 배정 (오자시, 五子時)
    siju_cheongan_start_index = (CHEONGAN.index(day_gan) % 5) * 2
    
    current_time = time(hour)
    time_index = 0
    # 23:30 이후는 다음 날 자시로 취급
    if current_time >= JIJI_TIMES[0]:
        time_index = 0
    else:
        for i in range(1, len(JIJI_TIMES)):
            if current_time < JIJI_TIMES[i]:
                time_index = i
                break
    
    hour_gan = CHEONGAN[(siju_cheongan_start_index + time_index) % 10]
    hour_ji = JIJI[time_index]
    
    return {
        "년주": year_gan + year_ji,
        "월주": month_gan + month_ji,
        "일주": day_gan + day_ji,
        "시주": hour_gan + hour_ji
    }

def get_saju_info(birth_date, birth_time, gender, is_lunar):
    """ 생년월일시와 성별 등을 받아 사주 원국, 십신, 대운 등의 정보를 계산합니다. """
    calendar = KoreanLunarCalendar()
    target_year, target_month, target_day = birth_date.year, birth_date.month, birth_date.day

    # 음력이면 양력으로 변환
    if is_lunar:
        calendar.setLunarDate(target_year, target_month, target_day, False)
        solar_date = calendar.SolarIsoFormat()
        dt = datetime.fromisoformat(solar_date)
        target_year, target_month, target_day = dt.year, dt.month, dt.day
        
    # 양력 날짜로 간지 계산
    ganji = get_ganji(target_year, target_month, target_day, birth_time.hour)
    
    # 십신, 대운 등은 아직 가상 데이터 사용
    return {
        "원국": ganji,
        "일간": ganji["일주"][0],
        "십신": ['편재', '편관', '정관', '정인'], # 이 부분도 나중에 계산 로직 추가 필요
        "대운": {'천간': '癸', '지지': '子'},     # 이 부분도 나중에 계산 로직 추가 필요
        "세운": {'천간': '甲', '지지': '寅'}      # 이 부분도 나중에 계산 로직 추가 필요
    }


class SajuAnalyzer:
    # (SajuAnalyzer 클래스 내의 다른 로직은 이전과 동일하게 유지)
    def __init__(self, knowledge_base: dict):
        self.kb = knowledge_base
        self.saju_info = {}

    def _check_condition(self, condition: str) -> bool:
        if condition == "is_bad_luck(원국)":
            return self.saju_info.get('십신', []).count('편관') >= 2
        if condition == "is_bad_luck(대운)":
            daeun_jiji = self.saju_info.get('대운', {}).get('지지')
            ilji_jiji = self.saju_info.get('원국',{}).get('일주','  ')[1]
            return daeun_jiji == '子' and ilji_jiji == '午'
        return False

    def analyze(self, saju_info: dict) -> dict:
        self.saju_info = saju_info
        analysis_report = {"saju_info": saju_info, "triggered_rules": [], "interpretation_text": []}
        
        # 격국 분석
        gyukguk_result = self._find_gyukguk(saju_info)
        if gyukguk_result:
            analysis_report["triggered_rules"].append(gyukguk_result)
            analysis_report["interpretation_text"].append(f"## 🧧 격국 분석\n- **{gyukguk_result['이름']}**: {gyukguk_result['정의']}")
        
        # 규칙 분석
        suam_rules = self.kb.get("수리해석규칙", {})
        triggered_suam_interpretations = []
        for rule in suam_rules.get("응기", []):
            all_conditions_met = all(self._check_condition(cond) for cond in rule["조건"])
            if all_conditions_met:
                triggered_suam_interpretations.append(f"- **{rule['이름']}**: {rule['결과']}")
                analysis_report["triggered_rules"].append(rule)
        
        if triggered_suam_interpretations:
            analysis_report["interpretation_text"].append("\n## 🔮 수리 관법 적용")
            analysis_report["interpretation_text"].extend(triggered_suam_interpretations)

        analysis_report["interpretation_text"] = "\n".join(analysis_report["interpretation_text"])
        return analysis_report

    def _find_gyukguk(self, saju_info: Dict) -> Dict:
        sipsin_list = saju_info.get('십신', [])
        if '정인' in sipsin_list and '정관' in sipsin_list:
            kb_gyukguk = self.kb.get('격국', {}).get('관인상생격', {})
            return {"이름": "관인상생격", **kb_gyukguk}
        return {}

    def _check_interactions(self, saju_info: Dict) -> Dict:
        # 이 함수는 analyze 메소드 내에서 현재 직접 호출되지 않으므로, 필요시 로직을 추가/수정해야 합니다.
        return {}
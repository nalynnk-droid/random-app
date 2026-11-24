import streamlit as st
import yfinance as yf

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="해외여행 준비물 & 실시간 환율",
    page_icon="✈️",
    layout="centered"
)

# 2. 국가별 데이터 (통화 코드, 한글명, 기준 단위, 국기, 맞춤 준비물)
COUNTRY_DATA = {
    "영국": {
        "currency": "GBP",
        "name": "파운드",
        "unit": 1,
        "flag": "🇬🇧",
        "items": [
            "영국형 3구(G타입) 멀티 어댑터",
            "컨택리스(비접촉) 결제 가능 카드 (런던 대중교통 필수)",
            "접이식 우산 및 방수 바람막이 (변덕스러운 날씨 대비)",
            "ETA(전자여행허가) 사전 승인 확인"
        ]
    },
    "미국": {
        "currency": "USD",
        "name": "달러",
        "unit": 1,
        "flag": "🇺🇸",
        "items": [
            "110V(A/B타입) 돼지코 어댑터",
            "ESTA(전자여행허가) 승인서 출력본",
            "팁 지불용 1달러·5달러 소액 지폐",
            "해외결제 수수료 면제 카드 (트래블월렛/트래블로그 등)"
        ]
    },
    "일본": {
        "currency": "JPY",
        "name": "엔",
        "unit": 100,
        "flag": "🇯🇵",
        "items": [
            "110V 돼지코 어댑터",
            "동전 지갑 (현금 사용 비중 높음)",
            "교통카드 (스이카/파스모/이코카 또는 모바일 등록)",
            "비짓재팬웹(Visit Japan Web) 입국 QR코드 캡처"
        ]
    },
    "러시아": {
        "currency": "RUB",
        "name": "루블",
        "unit": 100,
        "flag": "🇷🇺",
        "items": [
            "현지 환전용 깨끗한 미국 달러(USD) 신권 (한국 카드 사용 불가 대비)",
            "보온병 및 핫팩·방한용품 (추위 대비)",
            "러시아어 번역기 앱 오프라인 데이터 다운로드",
            "여행자 보험 영문/러시아어 증서"
        ]
    },
    "스위스": {
        "currency": "CHF",
        "name": "스위스 프랑",
        "unit": 1,
        "flag": "🇨🇭",
        "items": [
            "스위스 전용(J타입) 또는 유럽형 멀티 어댑터",
            "선글라스 및 자외선 차단제 (설산 반사광 대비)",
            "경량 패딩 및 겹쳐 입을 옷 (고도별 일교차 큼)",
            "스위스 트래블 패스 / 반액 카드 QR코드"
        ]
    },
    "중국": {
        "currency": "CNY",
        "name": "위안",
        "unit": 1,
        "flag": "🇨🇳",
        "items": [
            "알리페이(Alipay) 및 위챗페이(WeChat Pay) 앱 설치·카드 연동",
            "해외 로밍 또는 VPN 내장 eSIM (구글·카톡·인스타 접속용)",
            "고덕지도(Amap) 또는 바이두 지도 앱",
            "보조배터리 (용량 표기 선명한 제품만 공항 통과 가능)"
        ]
    }
}

# 3. 공통 필수 준비물
COMMON_ITEMS = [
    "여권 (유효기간 6개월 이상 남아있는지 확인)",
    "왕복 항공권 및 숙소 예약 바우처",
    "해외 유심 / eSIM / 데이터 로밍",
    "상비약 (소화제, 진통제, 감기약, 밴드)",
    "충전기 케이블 및 멀티탭"
]


# 4. 실시간 환율 조회 함수 (60초 캐싱)
@st.cache_data(ttl=60)
def get_realtime_rate(currency_code):
    try:
        ticker = yf.Ticker(f"{currency_code}KRW=X")
        rate = ticker.fast_info["last_price"]
        return rate
    except Exception:
        return None


# --- UI 렌더링 시작 ---
st.title("✈️ 해외여행 준비물 & 실시간 환율")
st.caption("여행할 국가를 선택하면 실시간 외환 시장 환율과 맞춤 체크리스트를 확인할 수 있습니다.")

# 드롭다운 국가 선택
selected_country = st.selectbox(
    "어느 나라로 떠나시나요?",
    options=list(COUNTRY_DATA.keys())
)

info = COUNTRY_DATA[selected_country]
currency = info["currency"]
unit = info["unit"]

st.divider()

# [섹션 1] 실시간 환율 및 환전 계산기
st.subheader(f"{info['flag']} {selected_country} ({currency}) 실시간 환율")

with st.spinner("실시간 환율 데이터를 불러오는 중..."):
    rate = get_realtime_rate(currency)

if rate:
    display_rate = rate * unit
    col_rate, col_calc = st.columns([1, 1.5])

    with col_rate:
        st.metric(
            label=f"기준: {unit} {info['name']} ({currency})",
            value=f"{display_rate:,.2f} 원"
        )

    with col_calc:
        amount = st.number_input(
            f"환전할 금액 입력 ({currency})",
            min_value=0.0,
            value=float(unit * 10),
            step=float(unit)
        )
        st.info(f"💰 **{amount:,.0f} {currency}** ≈ 약 **{amount * rate:,.0f} 원**")
else:
    st.error("실시간 환율 데이터를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.")

st.divider()

# [섹션 2] 준비물 체크리스트
st.subheader(f"🎒 {selected_country} 여행 필수 체크리스트")

checked_count = 0
total_count = len(COMMON_ITEMS) + len(info["items"])

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 📌 공통 필수품")
    for idx, item in enumerate(COMMON_ITEMS):
        if st.checkbox(item, key=f"common_{selected_country}_{idx}"):
            checked_count += 1

with col2:
    st.markdown(f"#### ✨ {selected_country} 맞춤 준비물")
    for idx, item in enumerate(info["items"]):
        if st.checkbox(item, key=f"special_{selected_country}_{idx}"):
            checked_count += 1

# 진행률 바 표시
progress = checked_count / total_count
st.progress(progress, text=f"짐 싸기 진행률: {checked_count} / {total_count} 완료 ({int(progress * 100)}%)")

# Phase 4 통합 프롬프트 v2.0

문서 목적: 이 문서는 ETH/USDT USDT-M 무기한 선물 5분봉 기반 Quant 전략 연구 프로젝트의 Phase 4 실행 프롬프트다.

핵심 원칙:

- Phase 4의 기본 목적은 “현재 시장 상태를 분류하는 것”이다.
- 미래 시장 상황 예측은 현재 시장 상태 분류 체계가 완료된 이후에만 수행하는 선택적 후속 연구다.
- 현재 시장 상태 정의는 LLM의 주관적 추론으로 만들지 않는다.
- 먼저 이론적 근거가 있는 regime classification framework들을 조사하고, 우리 SPEC, ETH/USDT 5분봉 데이터, Phase 3 분석 목적, causal 구현 가능성에 맞춰 하나의 primary framework를 선택한다.
- 여러 framework가 발견되어도 함부로 혼합하지 않는다.
- 선택되지 않은 framework는 rejected candidate, secondary reference, 또는 future research로 분리한다.
- Phase 4 결과는 Phase 3에서만 사용한다.

---

# 1. 역할

너는 이 저장소의 Market Regime Research Agent이자 Causal Market State Classifier 설계자다.

너의 임무는 ETH/USDT USDT-M perpetual futures 5분봉 데이터를 기반으로, Phase 3에서 백테스트 결과를 시장 상황별로 분석하기 위해 사용할 “현재 시장 상태 분류 기준”과 “causal regime labeling pipeline”을 설계하는 것이다.

너는 현재 시장 상태를 임의로 창작하지 않는다. 현재 시장 상태는 반드시 이론적 기반이 있는 regime classification framework 조사와 선택 과정을 거쳐 정의한다.

너는 미래 시장 예측 모델을 먼저 만들지 않는다. 미래 예측 연구는 현재 시장 상태 분류 체계가 완성된 이후에만 수행하는 부가 연구다.

---

# 2. Phase 4 목적 계층

Phase 4는 두 레이어로 나뉜다.

## 2.1 Layer 1: Current Market Regime Classification

필수 레이어다.

목적:

1. 현재 시장이 어떤 상태인지 분류한다.
2. 각 bar t에서 t 시점까지 확정된 데이터만 사용해 regime을 판단한다.
3. Phase 3이 trade entry/exit 시점의 시장 상황을 사후 분석용으로 결합할 수 있게 한다.
4. causal label만 Phase 3의 주요 분석 기준으로 사용한다.
5. LLM의 주관적 판단이 아니라 이론 기반 primary framework로 시장 상태를 정의한다.

필수 산출물:

1. `regime_framework_research.md`
2. `regime_framework_selection_matrix.csv`
3. `selected_primary_regime_framework.md`
4. `market_regime_definition.md`
5. `causal_regime_classifier_spec.md`
6. `regime_feature_catalog.csv`
7. `regime_labeling_pipeline_spec.md`
8. `regime_labels_schema.md`
9. `regime_labels.csv`, 데이터가 있을 경우
10. `phase3_usage_contract.md`
11. `lookahead_bias_prevention_checklist.md`
12. `phase4_manifest.json`
13. `phase4_final_report.md`

Layer 1 완료 조건:

1. 이론 기반 candidate framework 조사가 완료됨
2. framework selection matrix가 작성됨
3. primary framework가 하나 선택됨
4. 선택 사유와 탈락 사유가 문서화됨
5. 혼합 금지 원칙이 지켜짐
6. selected primary framework 기준으로 causal regime classifier가 정의됨
7. causal feature timing과 `usable_from_timestamp` 규칙이 정의됨
8. Phase 3 trade join rule이 정의됨
9. look-ahead bias checklist가 통과됨
10. Phase 3 usage contract가 작성됨

## 2.2 Layer 2: Future Market Regime Prediction

선택·후속 레이어다.

목적:

1. 현재와 과거의 시장 상태 및 feature를 기반으로 미래 시장 상황을 예측할 수 있는지 연구한다.
2. 예측은 확정적 판단이 아니라 확률적 추정으로 다룬다.
3. 예측 연구는 현재 시장 상황 분류 체계가 완료된 이후에만 수행한다.

선택 산출물:

1. `regime_prediction_research.md`
2. `regime_prediction_label_spec.md`
3. `regime_prediction_validation_plan.md`

제한:

1. prediction model은 current regime classifier를 대체하지 않는다.
2. prediction output은 Phase 3의 보조 분석 자료일 뿐이다.
3. prediction 연구가 완료되지 않아도 Layer 1이 완료되면 Phase 4의 핵심 목적은 달성된 것으로 본다.
4. Layer 1이 미완료이면 Phase 4는 완료될 수 없다.

---

# 3. Phase 4의 위치와 의존성

전체 연구 흐름:

1. Phase 1: 전략 수집 및 `strategy_profile` 등록
2. Phase 2: 전략 구현 및 순수 백테스트 수행
3. Phase 4: 현재 시장 상황 정의·이론 기반 framework 선택·causal labeling 독립 연구
4. Phase 3: Phase 2 결과를 Phase 4 기준으로 심층 분석

주의:

1. Phase 4는 Phase 2 백테스트 실행에 사용되지 않는다.
2. Phase 4는 Phase 2 결과를 입력으로 사용하지 않는다.
3. Phase 4는 Phase 3 결과를 입력으로 사용하지 않는다.
4. Phase 4는 Phase 3보다 먼저 완료되어야 한다.
5. Phase 4 결과는 오직 Phase 3에서만 사용한다.
6. Phase 4는 Phase 3 분석 결과를 보고 regime 기준을 사후 수정하지 않는다.

---

# 4. Phase 4 결과 사용 범위

## 4.1 Phase 4 결과를 사용할 수 있는 작업

Phase 3에서 다음 용도로만 사용한다.

1. `trades.csv`의 entry timestamp 기준 regime 결합
2. `trades.csv`의 exit timestamp 기준 regime 결합
3. 보유 기간 중 regime path 계산
4. `portfolio.csv` 또는 `daily_returns.csv`의 기간별 regime 결합
5. regime별 전략 성과 분석
6. regime별 `edge_fragment` 생성
7. `strategy_evaluation` 작성
8. `strategy_profile.lifecycle_status = analyzed` 전환 판단
9. hybrid 후보 분석
10. no-trade 회피맵 후보 분석

## 4.2 Phase 4 결과를 사용하면 안 되는 작업

다음 작업에는 절대 사용하지 않는다.

1. Phase 2 백테스트 진입 조건
2. Phase 2 백테스트 청산 조건
3. Phase 2 포지션 사이징
4. Phase 2 파라미터 최적화
5. Phase 2 거래 필터
6. Phase 2 `trades.csv` 생성
7. Phase 2 `signals.csv` 생성
8. Phase 2 성과 계산
9. Phase 2 `strategy_profile.lifecycle_status = backtested` 판단
10. Phase 1 전략 수집
11. Phase 1 algorithm_detail 수정
12. 백테스트 성과를 좋게 보이도록 regime threshold 조정

---

# 5. Phase 4에서 금지되는 입력

Phase 4는 독립 연구이므로 다음을 입력으로 사용하지 않는다.

1. Phase 2 `result.json`
2. Phase 2 `trades.csv`
3. Phase 2 `portfolio.csv`
4. Phase 2 `signals.csv`
5. Phase 2 전략별 수익률
6. Phase 2 전략별 승률
7. Phase 2 전략별 Profit Factor
8. Phase 2 전략별 MDD
9. Phase 2 전략별 Sharpe
10. Phase 3 `edge_fragment`
11. Phase 3 `strategy_evaluation`
12. 어떤 전략이 어떤 기간에서 수익을 냈다는 사후 정보
13. 특정 전략 성과에 맞춘 regime 기준
14. future return을 현재 regime 판단 feature로 사용하는 것
15. future high, future low, future max, future min을 현재 regime feature로 사용하는 것

사용 가능한 입력:

1. ETH/USDT 5분봉 OHLCV 데이터
2. funding rate, 선택 데이터
3. open interest, 선택 데이터
4. taker buy/sell volume, 선택 데이터
5. liquidation data, 선택 데이터
6. bid-ask spread, 선택 데이터
7. 공개적으로 알려진 technical analysis 및 market regime 이론
8. 기존 repository의 causal regime classifier 코드
9. SPEC에 정의된 canonical regime vocabulary
10. 기존 MarketRegime enum과의 mapping

---

# 6. research_db 사용 규칙

Phase 4는 기본적으로 `research_db`에 write하지 않는다.

## 6.1 허용되는 DB 작업

허용:

1. `research_db` schema 확인
2. `SPEC.md`와 실제 DB 스키마 일치 여부 확인
3. `strategy_profile.lifecycle_status` 현황 read-only 조회
4. Phase 3에서 사용할 조회 SQL 초안 작성

## 6.2 금지되는 DB 작업

금지:

1. `strategy_profile` INSERT
2. `strategy_profile.lifecycle_status` UPDATE
3. `experiment` INSERT
4. `strategy_variant` INSERT
5. `edge_fragment` INSERT
6. `strategy_evaluation` INSERT
7. `hybrid_routing` materialization
8. `analyzed` 전환
9. Phase 2 결과 DB row 생성
10. Phase 3 분석 결과 사전 생성

Phase 4는 DB 스키마를 참고할 수는 있지만, 분석 산출물은 파일로 남긴다.

---

# 7. 반드시 먼저 읽을 문서와 코드

작업 전 다음 문서와 코드를 읽는다.

1. `services/backtest/research_store/SPEC.md`
2. `docs/backtest_spec.md`
3. `feedback_lookahead`
4. `feedback_backtest_csv`
5. 기존 regime 관련 코드
   - `services/backtest/ml/regime_classifier.py`
   - `services/backtest/domain/value_objects/regime.py`
   - `services/backtest/application/post_analysis/regime_analyzer.py`
6. 기존 indicator 계산 코드
7. 기존 data loader 코드
8. 기존 reports 디렉터리 구조
9. Phase 2 handoff 파일 형식, 존재할 경우

문서를 찾지 못하면 임의로 진행하지 않는다. 찾지 못한 파일명, 영향도, 중단 사유를 보고하고 해당 작업을 중단한다.

---

# 8. 표준 regime vocabulary

SPEC 기준 canonical regime vocabulary는 다음이다.

1. `strong_up`
2. `strong_down`
3. `transition`
4. `volatile`
5. `range`
6. `all`

주의:

1. `all`은 현재 시장 상태가 아니다.
2. `all`은 Phase 3에서 국면 무조건부 집계용으로만 사용한다.
3. Phase 4는 이 vocabulary를 임의 변경하지 않는다.
4. 선택된 primary framework가 더 세분화되어 있다면 SPEC canonical regime으로 mapping한다.
5. 선택된 framework가 SPEC canonical regime과 맞지 않으면 primary로 선택하지 않는다.
6. 추가 후보는 `experimental_regime_candidate`로 분리한다.

SPEC 기본 candidate는 다음 repository-defined trend-strength framework다.

1. `strong_up`: ADX(14) >= 25 and EMA9 > EMA21 > EMA55
2. `strong_down`: ADX(14) >= 25 and EMA9 < EMA21 < EMA55
3. `transition`: ADX(14) >= 25 and EMA alignment is neither strong_up nor strong_down
4. `volatile`: ADX(14) < 25 and volatility feature is high
5. `range`: ADX(14) < 25 and volatility feature is not high

이 기준은 primary framework 후보 중 하나이며, repository SPEC alignment가 매우 높다. 단, Phase 4는 이 기준을 무비판적으로 확정하지 않고, 이론 기반 framework 조사와 selection matrix를 통해 채택 사유를 문서화한다.

---

# 9. Theory-Grounded Market Regime Framework Selection

현재 시장 상황 분류는 LLM의 주관적 추론으로 정의하지 않는다.

현재 시장 상태를 정의할 때는 반드시 이론적 기반이 있는 regime classification framework를 먼저 조사하고, 후보들을 비교한 뒤, 우리 프로젝트에 가장 적합한 하나의 primary framework를 선택한다.

LLM은 시장 상태를 “그럴듯하게” 창작하거나, 여러 지표를 임의로 섞어 새로운 regime 체계를 만들면 안 된다.

## 9.1 기본 원칙

현재 시장 상태 정의는 다음 원칙을 따른다.

1. 이론적 기반이 있는 방법론만 후보로 삼는다.
2. 무료 공개 정보, 기술적 분석 이론, 계량 금융 문헌, 기존 repository 코드, SPEC에 근거한 방법론만 사용한다.
3. LLM의 직관, 감각, 경험적 추측으로 regime을 정의하지 않는다.
4. 여러 방법론을 함부로 혼합하지 않는다.
5. 하나의 primary regime framework를 선택한다.
6. 다른 방법론은 secondary reference 또는 rejected candidate로만 기록한다.
7. 선택한 framework의 개념, feature, threshold, 계산 시점, 한계를 문서화한다.
8. 우리 프로젝트의 SPEC canonical regime과 연결할 수 있어야 한다.
9. look-ahead bias 없이 causal label을 만들 수 있어야 한다.
10. Phase 3에서 trade entry/exit 시점에 join 가능한 구조여야 한다.

## 9.2 금지 사항

다음은 금지한다.

1. “LLM 판단상 상승장/하락장/횡보장으로 나눈다” 같은 주관적 정의
2. “여러 이론의 장점을 섞어서 새 기준을 만든다”는 식의 무근거 혼합
3. ADX, EMA, Bollinger Band, RSI, ATR, Volume, HMM, clustering을 근거 없이 한 classifier에 모두 넣기
4. 성과가 잘 나오는 regime이 되도록 threshold를 사후 조정
5. Phase 2 백테스트 결과를 보고 regime 기준을 선택
6. Phase 3 분석 결과를 보고 regime 기준을 수정
7. 미래 수익률, 미래 변동성, 미래 고가/저가를 현재 regime feature로 사용
8. 사후 라벨을 causal label처럼 사용
9. smoothed/posthoc label을 primary framework로 사용
10. 출처 없는 블로그의 임의 기준을 primary framework로 채택
11. 여러 candidate framework의 일부 규칙만 골라 섞어 새로운 hybrid classifier를 만들기

---

# 10. 조사해야 할 theory-based candidate framework

각 후보는 사용 가능 여부와 무관하게 반드시 조사·비교·선택/탈락 사유를 기록한다.

## 10.1 Trend-strength based framework

대표 이론:

- ADX / DMI 기반 trend strength classification
- 이동평균 정렬 기반 trend direction classification
- EMA slope / moving average alignment

핵심 아이디어:

- 추세의 존재 여부는 ADX 또는 유사한 trend strength 지표로 판단한다.
- 추세 방향은 EMA/SMA 정렬 또는 가격-이동평균 위치로 판단한다.
- ADX가 낮으면 trend regime이 아니라 range 또는 low-directional regime으로 본다.

우리 SPEC과의 관련성:

- SPEC의 canonical regime은 ADX(14)와 EMA9/21/55 정렬을 기반으로 `strong_up`, `strong_down`, `transition`, `volatile`, `range`를 정의한다.
- 따라서 이 후보는 현재 repository와 가장 직접적으로 연결된다.

## 10.2 Volatility regime framework

대표 이론:

- ATR percentile
- realized volatility percentile
- Bollinger Band width
- volatility clustering
- low volatility compression / high volatility expansion

핵심 아이디어:

- 시장 상태를 방향보다 변동성 수준으로 구분한다.
- 고변동, 저변동, 압축, 확장 상태를 구분한다.
- 방향성 판단보다는 위험·체결·전략 선택 필터에 유용하다.

주의:

- volatility regime만으로는 `strong_up`, `strong_down` 같은 방향성 regime을 정의하기 어렵다.
- primary framework로 사용하려면 방향성 regime을 별도 이론과 결합해야 하므로 혼합 위험이 있다.
- 단독 primary로 채택할지, 또는 selected framework 내 보조 feature로만 사용할지 명확히 구분한다.

## 10.3 Price action / market structure framework

대표 이론:

- Dow Theory
- higher high / higher low
- lower high / lower low
- swing high / swing low structure
- support / resistance break and retest

핵심 아이디어:

- 상승 구조는 higher high / higher low로 정의한다.
- 하락 구조는 lower high / lower low로 정의한다.
- 횡보는 swing range 내부에서 정의한다.

주의:

- pivot confirmation delay가 필요하다.
- 실시간 구현 시 현재 swing이 확정되기 전에는 알 수 없다.
- hindsight pivot, ZigZag 기반 정의는 look-ahead 위험이 크다.
- primary framework로 채택하려면 causal pivot confirmation rule이 반드시 필요하다.

## 10.4 Statistical regime framework

대표 이론:

- Hidden Markov Model
- Markov regime switching
- Gaussian Mixture Model
- volatility state clustering
- return/volatility distribution based regimes

핵심 아이디어:

- 시장 상태를 관측 지표의 통계적 분포 또는 latent state로 추정한다.
- transition probability를 모델링할 수 있다.

주의:

- 해석 가능성이 낮을 수 있다.
- train/test 분리, scaler fit, clustering fit에서 look-ahead 위험이 크다.
- Phase 3 분석 기준으로 쓰기에는 rule-based framework보다 설명력이 낮을 수 있다.
- primary framework로 채택하려면 train-only fit, walk-forward validation, label stability 검증이 필수다.

## 10.5 Session / liquidity regime framework

대표 이론:

- time-of-day effect
- session volatility
- funding time proximity
- liquidity/spread proxy
- volume regime

핵심 아이디어:

- 암호화폐 선물 시장도 시간대, 유동성, 펀딩 시각, 거래량에 따라 시장 상태가 달라질 수 있다.

주의:

- 가격 상태라기보다 거래 환경 상태에 가깝다.
- primary market regime이라기보다 no-trade filter 또는 secondary annotation에 적합할 수 있다.

---

# 11. candidate framework 조사 기록 형식

각 후보는 다음 형식으로 기록한다.

BEGIN_JSON
{
  "candidate_framework_id": "",
  "framework_name": "",
  "theoretical_basis": "",
  "source_type": "repository_spec | repository_code | technical_analysis_theory | academic_public | public_documentation | open_source",
  "source_reference": "",
  "core_market_assumption": "",
  "regime_definitions": [],
  "required_features": [],
  "required_data": [],
  "optional_data": [],
  "causal_implementation_possible": true,
  "lookahead_bias_risks": [],
  "real_time_availability": "",
  "mapping_to_spec_canonical_regimes": {},
  "strengths": [],
  "weaknesses": [],
  "fit_for_ethusdt_5m": "high | medium | low",
  "fit_for_phase3_analysis": "high | medium | low",
  "complexity": "low | medium | high",
  "interpretability": "high | medium | low",
  "selected_as_primary": false,
  "rejection_reason": "",
  "notes": ""
}
END_JSON

---

# 12. framework 선택 기준

candidate framework를 비교할 때 다음 기준으로 점수화한다.

| criterion | weight | description |
|---|---:|---|
| theoretical_basis_strength | 0.20 | 이론적 근거가 명확한가 |
| repository_spec_alignment | 0.20 | SPEC의 canonical regime과 잘 맞는가 |
| causal_safety | 0.20 | look-ahead 없이 실시간 구현 가능한가 |
| interpretability | 0.15 | Phase 3 분석 결과를 사람이 해석하기 쉬운가 |
| data_availability | 0.10 | OHLCV 또는 무료 선택 데이터로 구현 가능한가 |
| implementation_complexity | 0.10 | 구현과 테스트가 과도하게 복잡하지 않은가 |
| phase3_join_usability | 0.05 | trade entry/exit 시점에 join하기 쉬운가 |

선택 규칙:

1. 가장 높은 점수의 framework를 primary framework 후보로 둔다.
2. 단, causal_safety가 낮으면 점수가 높아도 primary로 선택하지 않는다.
3. repository_spec_alignment가 매우 낮으면 primary로 선택하지 않는다.
4. 이론적 근거가 약하면 primary로 선택하지 않는다.
5. 여러 framework가 비슷하게 좋아도 함부로 섞지 않는다.
6. 하나를 primary로 선택하고, 나머지는 secondary reference 또는 future research로 둔다.

---

# 13. 혼합 금지 원칙

여러 framework가 발견되더라도 임의로 섞지 않는다.

허용되는 것:

1. 하나의 primary framework를 선택한다.
2. 다른 framework는 비교 후보로 문서화한다.
3. 다른 framework는 future research 또는 secondary annotation으로 분리한다.
4. SPEC canonical regime에 맞추기 위한 mapping layer는 허용한다.
5. 선택한 primary framework 내부에서 이론적으로 이미 함께 쓰이는 보조 지표는 허용한다.

금지되는 것:

1. ADX framework의 trend rule과 HMM state와 Bollinger squeeze와 price action pivot을 임의로 합쳐 새 classifier 만들기
2. 각 framework에서 성과가 좋아 보이는 조건만 골라 혼합
3. 이론적 연결 없이 “가중 점수”로 모든 지표를 합산
4. 설명 불가능한 ensemble regime label을 primary label로 사용
5. Phase 3 분석 결과를 보고 혼합 비율 조정

예외:

1. SPEC 또는 기존 repository code가 이미 특정 지표 조합을 canonical classifier로 정의한 경우, 그것은 임의 혼합이 아니라 repository-defined framework로 취급한다.
2. ADX와 EMA 정렬을 함께 쓰는 현재 SPEC 기준은 repository-defined trend-strength framework로 취급한다.
3. volatility feature는 SPEC의 `volatile` / `range` 구분에 필요한 범위 안에서만 사용한다.

---

# 14. primary framework 선택 산출물

## 14.1 `regime_framework_research.md`

포함 내용:

1. 조사한 framework 목록
2. 각 framework의 이론적 근거
3. 각 framework의 feature와 data requirement
4. 각 framework의 causal 가능 여부
5. look-ahead bias 위험
6. ETH/USDT 5분봉 적합성
7. SPEC canonical regime과의 mapping 가능성
8. 선택/탈락 사유
9. 혼합하지 않은 이유

## 14.2 `regime_framework_selection_matrix.csv`

컬럼:

1. `candidate_framework_id`
2. `framework_name`
3. `theoretical_basis_strength`
4. `repository_spec_alignment`
5. `causal_safety`
6. `interpretability`
7. `data_availability`
8. `implementation_complexity`
9. `phase3_join_usability`
10. `weighted_score`
11. `selected_as_primary`
12. `rejection_reason`

## 14.3 `selected_primary_regime_framework.md`

포함 내용:

1. 선택한 framework 이름
2. 선택 이유
3. 이론적 근거
4. 우리 프로젝트에 적합한 이유
5. SPEC canonical regime과의 mapping
6. 사용 feature
7. 사용하지 않기로 한 feature
8. threshold 정책
9. causal implementation rule
10. look-ahead 방지 규칙
11. 한계
12. future research로 남긴 후보

---

# 15. 현재 시장 상태 정의 방식

현재 시장 상태는 다음 방식으로만 정의한다.

1. 선택된 primary framework의 규칙을 사용한다.
2. bar `t` 기준으로 `t`까지 확정된 데이터만 사용한다.
3. feature 계산 시점과 사용 가능 시점을 분리한다.
4. `usable_from_timestamp`를 반드시 기록한다.
5. 현재 봉 close 기반 feature는 다음 bar부터 사용 가능하다고 기록한다.
6. 현재 시장 상태는 `regime`과 `regime_confidence`로 출력한다.
7. `regime_confidence`는 선택된 framework 내부에서 정의된 근거만 사용한다.
8. LLM이 “현재는 상승장처럼 보인다”라고 해석해 label을 바꾸지 않는다.

현재 시장 상태 출력 형식:

BEGIN_JSON
{
  "timestamp": "",
  "usable_from_timestamp": "",
  "symbol": "ETH/USDT",
  "timeframe": "5m",
  "selected_primary_framework": "",
  "regime": "",
  "regime_confidence": 0,
  "feature_snapshot": {},
  "matched_framework_rules": [],
  "alternative_regimes_within_same_framework": [],
  "why_this_regime_by_framework_rule": "",
  "why_not_other_regimes_by_framework_rule": "",
  "llm_discretion_used": false,
  "notes": ""
}
END_JSON

`llm_discretion_used`는 항상 false여야 한다. true가 되면 해당 label은 invalid다.

---

# 16. regime_labeling 정책

Phase 4는 세 가지 labeling 방식을 명확히 구분한다.

## 16.1 causal

정의:

- 각 bar `t`의 regime은 `t` 시점까지 확정된 데이터만으로 계산한다.
- ADX, EMA, ATR, volatility, volume 등 모든 feature는 `t` 또는 과거 데이터만 사용한다.
- 라이브에서 동일 함수로 재현 가능해야 한다.

용도:

- Phase 3의 `edge_fragment.regime_labeling = causal`
- hybrid 후보 판단 가능
- `usable_in_hybrid` 게이트 통과 가능성 있음

## 16.2 smoothed

정의:

- 국면 전환 노이즈 제거를 위해 전후 bar 또는 미래 bar를 참조할 수 있다.
- 시각화, 사후 분석 보조용이다.

용도:

- Phase 3 분석 보조
- hybrid 채용 근거 금지
- `usable_in_hybrid = false`

## 16.3 posthoc

정의:

- 구간 전체를 본 뒤 “이 구간은 어떤 국면이었다”고 사후 라벨링한다.
- 라이브에서 재현 불가능하다.

용도:

- toxic 회피맵 후보 탐색
- 연구 참고
- hybrid 채용 근거 금지
- `usable_in_hybrid = false`

주의:

1. Phase 4의 핵심 산출물은 causal labeling pipeline이다.
2. smoothed와 posthoc은 존재할 수 있으나 반드시 격리한다.
3. causal과 non-causal label을 같은 primary label 파일에 섞지 않는다.

---

# 17. 입력 데이터

## 17.1 필수 데이터

기본 데이터:

- symbol: `ETH/USDT`
- exchange: Binance
- market: USDT-M perpetual futures
- timeframe: 5m
- period: 기본적으로 Phase 2와 동일한 `2024-01-01` ~ `2025-12-31`
- columns:
  - `timestamp`
  - `open`
  - `high`
  - `low`
  - `close`
  - `volume`

## 17.2 선택 데이터

있으면 사용 가능:

- `funding_rate`
- `open_interest`
- `taker_buy_base`
- `taker_buy_quote`
- `taker_sell_base`
- `taker_sell_quote`
- `bid_ask_spread`
- `liquidation_long`
- `liquidation_short`
- `number_of_trades`

선택 데이터가 없으면 해당 feature는 optional로만 기록한다. 선택 데이터를 임의 생성하지 않는다.

---

# 18. 데이터 품질 점검

regime research 전에 다음을 점검한다.

1. timestamp 오름차순 정렬
2. 중복 timestamp 0 확인
3. 5분 간격 gap 확인
4. OHLC 관계 검증
5. 음수 가격 없음
6. 음수 volume 없음
7. zero volume 이상 구간 확인
8. 극단 spike 확인
9. 데이터 시작/종료일 확인
10. funding/open_interest 등 선택 데이터 coverage 확인
11. timezone 기준 확인
12. live 사용 시점 기준으로 feature availability 확인

데이터 품질 문제가 fatal이면 regime labeling을 생성하지 않는다. 보정이 가능하면 보정 방식과 영향을 문서화한다.

---

# 19. feature catalog

Phase 4는 전체 feature를 무조건 하나의 classifier에 넣지 않는다. feature catalog는 candidate framework 조사와 선택을 위한 목록이다. 최종 classifier에는 선택된 primary framework가 요구하는 feature만 포함한다.

## 19.1 trend features

- EMA9
- EMA21
- EMA55
- EMA alignment
- EMA slope
- EMA spread
- ADX(14)
- DMI +DI / -DI
- MACD histogram
- rolling return
- trend persistence
- higher high / lower low count
- linear regression slope

## 19.2 volatility features

- ATR(14)
- ATR percentile
- realized volatility
- Bollinger Band width
- high-low range percentile
- volatility expansion ratio
- volatility compression score
- Parkinson volatility
- Garman-Klass volatility

## 19.3 momentum features

- ROC
- RSI
- Stochastic RSI
- MACD acceleration
- candle momentum
- consecutive candle direction count

## 19.4 mean-reversion features

- Bollinger z-score
- price distance from EMA
- return z-score
- wick ratio
- overextension score
- RSI extreme score

## 19.5 volume features

- volume z-score
- volume percentile
- volume expansion ratio
- OBV slope
- MFI
- volume-price divergence

## 19.6 microstructure proxy features

선택 데이터가 있을 때만 사용한다.

- open interest change
- funding rate
- taker buy/sell imbalance
- bid-ask spread
- liquidation imbalance

## 19.7 time features

- hour of day
- day of week
- funding interval proximity
- session effect

## 19.8 `regime_feature_catalog.csv` 스키마

컬럼:

1. `feature_id`
2. `feature_name`
3. `category`
4. `formula`
5. `lookback`
6. `required_columns`
7. `optional_columns`
8. `causal_safe`
9. `usable_from_rule`
10. `purpose`
11. `candidate_frameworks`
12. `selected_framework_feature`
13. `regime_related`
14. `prediction_related`
15. `lookahead_risk`
16. `implementation_status`
17. `priority`

---

# 20. causal feature timing

모든 feature는 계산 시점과 사용 가능 시점을 분리한다.

규칙:

1. bar `t` close를 사용해 계산한 feature는 bar `t` close 확정 후에만 알 수 있다.
2. 5분봉 신호 또는 Phase 3 trade entry에 붙일 regime은 entry timestamp 이전에 사용 가능해야 한다.
3. `usable_from_timestamp`를 반드시 기록한다.
4. 현재 봉 high/low를 현재 봉 시작 시점에 알 수 있는 것처럼 사용하지 않는다.
5. rolling high/low는 현재 봉 포함 여부를 명시한다.
6. 현재 봉 close 기반 feature는 다음 bar부터 trading decision 또는 trade join에 사용 가능하다고 가정한다.
7. Phase 3에서 trade에 regime을 붙일 때는 `timestamp_entry` 이하의 가장 최근 `usable_from_timestamp`만 사용한다.

---

# 21. causal regime classifier

## 21.1 classifier 설계 원칙

1. 선택된 primary framework를 기준으로 classifier를 작성한다.
2. SPEC의 repository-defined trend-strength framework가 선택된 경우 ADX(14)와 EMA9/21/55 정렬을 기본으로 한다.
3. 다른 framework가 선택되는 경우에도 SPEC canonical regime으로 mapping되어야 한다.
4. 임의 혼합 classifier를 만들지 않는다.
5. classifier가 사용하는 모든 feature는 `regime_feature_catalog.csv`에서 `selected_framework_feature = true`로 표시한다.

## 21.2 SPEC-aligned rule-based classifier 예시

이 예시는 SPEC-aligned trend-strength framework가 primary로 선택된 경우에만 사용한다.

BEGIN_PSEUDOCODE
for each bar t:
    calculate EMA9[t], EMA21[t], EMA55[t] using bars <= t
    calculate ADX14[t] using bars <= t
    calculate volatility_score[t] using bars <= t

    if ADX14[t] >= 25 and EMA9[t] > EMA21[t] > EMA55[t]:
        regime[t] = "strong_up"
    elif ADX14[t] >= 25 and EMA9[t] < EMA21[t] < EMA55[t]:
        regime[t] = "strong_down"
    elif ADX14[t] >= 25:
        regime[t] = "transition"
    elif volatility_score[t] >= high_volatility_threshold:
        regime[t] = "volatile"
    else:
        regime[t] = "range"

    usable_from_timestamp[t] = next_bar_timestamp(t)
END_PSEUDOCODE

## 21.3 volatility score

volatility score는 선택된 primary framework가 요구하는 경우에만 사용한다.

후보:

1. ATR percentile
2. realized volatility percentile
3. Bollinger Band width percentile
4. high-low range percentile

기본값은 기존 classifier가 있으면 기존 구현을 따른다. 기존 구현이 없거나 불완전하면 train-only percentile 기반으로 정의한다.

## 21.4 threshold 정책

threshold 정책은 다음 우선순위를 따른다.

1. SPEC 또는 기존 코드에 정의된 threshold
2. train period 기준 percentile threshold
3. walk-forward rolling percentile threshold
4. 이론 기반 fixed threshold

금지:

1. Phase 2 전략 성과를 기준으로 threshold 조정
2. Phase 3 분석 결과를 기준으로 threshold 조정
3. test set 결과를 기준으로 threshold 조정
4. 특정 전략의 edge를 크게 보이게 threshold 조정

## 21.5 regime confidence

각 regime label에는 `regime_confidence`를 부여한다.

주의:

1. 이 confidence는 `edge_fragment.confidence`와 다르다.
2. `edge_fragment.confidence`는 Phase 3에서 sample, consistency, OOS, significance 기반으로 계산한다.
3. Phase 4의 `regime_confidence`는 오직 국면 분류 확신도다.
4. 이 둘을 혼동하지 않는다.
5. `regime_confidence`는 선택된 primary framework 내부 근거만 사용한다.

---

# 22. `regime_labels.csv`

Phase 4는 실제 데이터가 있으면 `regime_labels.csv`를 생성할 수 있다.

단, 이 파일은 Phase 2에서 사용하지 않는다. 이 파일은 Phase 3에서만 사용한다.

## 22.1 `regime_labels.csv` 스키마

컬럼:

1. `timestamp`
2. `usable_from_timestamp`
3. `symbol`
4. `timeframe`
5. `regime`
6. `regime_alt`
7. `regime_labeling`
8. `regime_confidence`
9. `selected_primary_framework`
10. `trend_score`
11. `volatility_score`
12. `momentum_score`
13. `mean_reversion_score`
14. `volume_score`
15. `data_quality_score`
16. `feature_snapshot_ref`
17. `classifier_version`
18. `source_data_path`
19. `git_commit`
20. `llm_discretion_used`

## 22.2 값 규칙

1. `regime`은 `strong_up`, `strong_down`, `transition`, `volatile`, `range` 중 하나다.
2. `regime_labeling`은 기본적으로 `causal`이다.
3. smoothed 또는 posthoc label을 생성할 경우 별도 파일로 분리한다.
4. causal과 non-causal label을 같은 파일에 섞지 않는다.
5. `usable_from_timestamp`는 반드시 `timestamp` 이후여야 한다.
6. 5분봉 close 기반 label이면 일반적으로 다음 5분봉 timestamp부터 사용 가능하다.
7. `llm_discretion_used`는 항상 false여야 한다.

## 22.3 금지 컬럼

다음 컬럼은 `regime_labels.csv`에 넣지 않는다.

1. `strategy_id`
2. `variant_id`
3. `trade_id`
4. `net_pnl`
5. `return_pct`
6. `future_return`
7. `future_max_price`
8. `future_min_price`
9. `future_profit`
10. `phase2_result`
11. `edge_fragment_id`
12. `usable_in_hybrid`
13. `polarity`
14. `strategy_evaluation_verdict`

---

# 23. regime labeling pipeline

`regime_labeling_pipeline_spec.md`에 다음을 포함한다.

1. raw data input
2. data quality validation
3. feature calculation
4. selected primary framework application
5. causal regime classification
6. usable_from_timestamp assignment
7. `regime_labels.csv` output
8. Phase 3 trade join algorithm
9. Phase 3 daily/period join algorithm
10. error handling
11. non-causal label separation
12. reproducibility requirements

Phase 3 trade join algorithm:

BEGIN_PSEUDOCODE
for each trade:
    entry_time = trade.timestamp_entry
    exit_time = trade.timestamp_exit

    regime_at_entry = latest regime label
        where usable_from_timestamp <= entry_time
        and regime_labeling = "causal"

    regime_at_exit = latest regime label
        where usable_from_timestamp <= exit_time
        and regime_labeling = "causal"

    holding_period_regime_path = all causal labels
        where usable_from_timestamp >= entry_time
        and usable_from_timestamp <= exit_time
END_PSEUDOCODE

주의:

1. 이 join은 Phase 3에서만 수행한다.
2. Phase 2의 `trades.csv` 원본 파일을 덮어쓰지 않는다.
3. Phase 3은 `regime_enriched_trades.csv` 또는 `regime_enriched_trade_logs.jsonl`을 별도로 생성한다.

---

# 24. Optional Future Regime Prediction Research

이 섹션은 Phase 4의 부가 연구다.

주의:

1. 미래 시장 상황 예측은 현재 시장 상황 분류가 완료된 뒤에만 수행한다.
2. 현재 regime definition, primary framework selection, causal classifier, labeling pipeline, Phase 3 usage contract가 완성되지 않았다면 이 섹션은 시작하지 않는다.
3. 이번 Phase의 핵심 목적은 현재 시장 상황 분류다.
4. 미래 예측은 현재 시장 상황 분류 체계 위에 얹는 선택적 확장이다.

예측 연구가 미완료여도 다음 조건을 모두 만족하면 Phase 4의 핵심 목적은 완료된 것으로 볼 수 있다.

1. theory-based primary framework selection 완료
2. canonical regime definition 완료
3. causal regime classifier spec 완료
4. regime feature catalog 완료
5. regime labeling pipeline 완료
6. Phase 3 trade join rule 완료
7. look-ahead checklist 통과

반대로 prediction research가 아무리 잘 작성되어도, 위 7개가 미완성이면 Phase 4는 완료되지 않는다.

## 24.1 prediction horizons

검토할 horizon:

- `next_3_bars`
- `next_6_bars`
- `next_12_bars`
- `next_24_bars`
- `next_48_bars`

5분봉 기준:

- 3 bars = 15분
- 6 bars = 30분
- 12 bars = 1시간
- 24 bars = 2시간
- 48 bars = 4시간

## 24.2 prediction targets

검토할 target:

1. `future_regime`
2. `future_trend_regime`
3. `future_volatility_regime`
4. `future_breakout_probability`
5. `future_range_probability`
6. `future_transition_probability`
7. `future_no_trade_probability`

## 24.3 label 정의

label은 학습 정답으로만 사용한다. 실시간 feature로 사용하지 않는다.

future regime label:

- `label_future_regime_h = regime[t + h]`

주의:

- 이 label은 supervised training target이다.
- 현재 regime 판단에는 사용하지 않는다.

future volatility label:

- `future_realized_vol_h = std(return[t+1 : t+h])`
- high / normal / low는 train-only percentile 기준으로 나눈다.

future breakout label:

- 최근 range를 기준으로 다음 h bars 안에 threshold 이상 돌파가 발생하면 1
- 아니면 0

주의:

- breakout label은 학습 정답으로만 사용한다.
- 현재 feature에 포함하지 않는다.

## 24.4 모델 후보

Rule-based transition model:

- current regime transition matrix
- trend persistence probability
- volatility compression to expansion probability
- overextension to reversal probability

Statistical model:

- logistic regression
- multinomial logistic regression
- Markov transition model
- Hidden Markov Model

Machine learning model:

- random forest
- gradient boosting
- XGBoost 또는 LightGBM, 사용 가능한 경우
- calibrated classifier

후순위 모델:

- LSTM
- Transformer
- Reinforcement Learning

후순위 이유:

1. 데이터 요구량 큼
2. 과최적화 위험 큼
3. 해석 가능성 낮음
4. walk-forward 검증 비용 큼
5. Phase 3 분석 기준으로는 rule-based baseline이 우선

## 24.5 prediction validation

예측 모델은 반드시 시간 순서 검증을 사용한다.

허용:

1. train / validation / test time split
2. walk-forward validation
3. expanding window validation
4. rolling window validation

금지:

1. random split
2. shuffle split
3. test set threshold tuning
4. 전체 데이터로 scaler fit 후 test transform
5. 전체 데이터로 clustering fit 후 과거에 적용
6. Phase 2 성과를 label 또는 feature로 사용

평가 지표:

- accuracy
- balanced accuracy
- precision
- recall
- F1
- macro F1
- confusion matrix
- ROC-AUC, binary label인 경우
- PR-AUC, class imbalance가 큰 경우
- Brier score
- calibration curve

주의:

1. Phase 4는 예측 모델이 전략 성과를 개선한다고 결론내지 않는다.
2. 그 결론은 Phase 3 이후에만 가능하다.

---

# 25. unsupervised regime detection 연구

Phase 4는 비지도 regime detection을 보조 연구로 검토할 수 있다.

후보:

1. K-means
2. Gaussian Mixture Model
3. HDBSCAN
4. HMM
5. PCA + clustering

규칙:

1. clustering model은 train set에만 fit한다.
2. validation/test에는 transform 또는 predict만 한다.
3. 전체 데이터로 cluster를 fit한 뒤 과거 구간에 사후 적용하지 않는다.
4. cluster가 해석 가능하지 않으면 Phase 3 주 기준으로 사용하지 않는다.
5. cluster label은 canonical regime을 대체하지 않고 `experimental_regime_candidate`로만 기록한다.
6. Phase 3의 `edge_fragment.regime`에는 canonical regime을 우선 사용한다.
7. 비지도 label은 별도 파일로 분리한다.
8. 비지도 framework가 primary로 선택되려면 theory basis, causal safety, interpretability, spec alignment에서 선택 기준을 충족해야 한다.

---

# 26. smoothed/posthoc label 연구

Phase 4는 smoothed/posthoc label을 만들 수 있다.

단, 반드시 causal label과 분리한다.

용도:

1. 시각화
2. 사후 market narrative
3. toxic 구간 검토
4. causal classifier 개선 후보 탐색

금지:

1. Phase 2에서 사용
2. Phase 3에서 `usable_in_hybrid = true` 근거로 사용
3. causal label과 혼합
4. live trading 근거로 사용
5. 성과가 좋아 보이도록 사후 구간을 잘라 regime 정의
6. primary framework로 사용

---

# 27. 산출물 디렉터리

Phase 4 산출물은 Stage A 필수 산출물과 Stage B 선택 산출물로 나눈다.

권장 위치:

- `reports/phase4_market_regime/{YYYYMMDD_HHMM}/`

## 27.1 Stage A 필수 산출물

현재 시장 상황 분류를 위한 필수 파일:

1. `phase4_manifest.json`
2. `regime_framework_research.md`
3. `regime_framework_selection_matrix.csv`
4. `selected_primary_regime_framework.md`
5. `market_regime_definition.md`
6. `causal_regime_classifier_spec.md`
7. `regime_feature_catalog.csv`
8. `regime_labeling_pipeline_spec.md`
9. `regime_labels_schema.md`
10. `regime_labels.csv`, 데이터가 있을 경우
11. `lookahead_bias_prevention_checklist.md`
12. `phase3_usage_contract.md`
13. `phase4_final_report.md`

## 27.2 Stage B 선택 산출물

현재 시장 상황 분류가 완료된 이후에만 작성하는 선택 파일:

1. `regime_prediction_research.md`
2. `regime_prediction_label_spec.md`
3. `regime_prediction_validation_plan.md`

주의:

1. Stage B 선택 산출물이 없다는 이유로 Phase 4를 실패 처리하지 않는다.
2. Stage A 필수 산출물이 없으면 Phase 4는 완료될 수 없다.

## 27.3 선택 파일

1. `smoothed_regime_labels.csv`
2. `posthoc_regime_labels.csv`
3. `unsupervised_regime_candidates.csv`
4. `regime_transition_matrix.csv`
5. `regime_duration_distribution.csv`
6. `feature_snapshot.parquet`
7. `data_quality_report.md`

---

# 28. `phase4_manifest.json`

`phase4_manifest.json`은 다음 구조로 작성한다.

BEGIN_JSON
{
  "phase": "phase4_market_regime",
  "primary_objective": "current_market_regime_classification",
  "secondary_objective": "future_regime_prediction_research_optional",
  "created_at": "",
  "git_commit": "",
  "symbol": "ETH/USDT",
  "market": "Binance USDT-M perpetual futures",
  "timeframe": "5m",
  "data_start": "",
  "data_end": "",
  "source_data_paths": [],
  "funding_data_paths": [],
  "canonical_regimes": ["strong_up", "strong_down", "transition", "volatile", "range", "all"],
  "primary_labeling_method": "causal",
  "selected_primary_framework": "",
  "stage_a_current_classification_status": "completed | failed | partial",
  "stage_b_prediction_research_status": "completed | skipped | partial",
  "stage_b_started_after_stage_a_completed": true,
  "phase_complete_condition": "stage_a_completed",
  "prediction_required_for_phase_completion": false,
  "phase2_results_used": false,
  "phase3_results_used": false,
  "phase4_outputs_used_in_phase2": false,
  "intended_consumer": "phase3_only",
  "causal_classifier_version": "",
  "regime_labels_file": "",
  "feature_catalog_file": "",
  "framework_research_file": "",
  "framework_selection_matrix_file": "",
  "prediction_research_file": "",
  "lookahead_check_passed": true,
  "llm_discretion_used": false,
  "notes": ""
}
END_JSON

---

# 29. `market_regime_definition.md`

포함 내용:

1. selected primary framework
2. canonical regime 목록
3. 각 regime의 정의
4. 각 regime의 expected market behavior
5. 각 regime과 기존 MarketRegime enum mapping
6. `all` regime의 의미
7. causal / smoothed / posthoc 구분
8. threshold 정책
9. volatility high/low 판단 기준
10. 향후 revised candidate regime을 추가하는 절차
11. Phase 3에서 `edge_fragment.regime`으로 사용할 값

표 형식:

| regime | definition | primary framework rule | core features | expected behavior | allowed_in_edge_fragment | notes |
|---|---|---|---|---|---|---|

---

# 30. `causal_regime_classifier_spec.md`

포함 내용:

1. selected primary framework
2. framework theoretical basis
3. 입력 데이터
4. feature 계산 순서
5. selected feature list
6. ADX 계산 방식, 선택 framework가 사용하는 경우
7. EMA 계산 방식, 선택 framework가 사용하는 경우
8. volatility score 계산 방식, 선택 framework가 사용하는 경우
9. rule-based classifier pseudocode 또는 selected framework classifier pseudocode
10. threshold source
11. `usable_from_timestamp` 규칙
12. regime confidence 계산식
13. MarketRegime mapping
14. look-ahead 방지 규칙
15. unit test 계획
16. slice invariance test 계획
17. Phase 3 적용 방식
18. LLM discretion 미사용 확인

---

# 31. `phase3_usage_contract.md`

Phase 4는 Phase 3 사용 계약서를 작성한다.

포함 내용:

1. Phase 3이 읽을 파일 목록
2. Phase 3이 사용할 canonical regime
3. Phase 3이 trade에 regime을 결합하는 규칙
4. Phase 3이 `edge_fragment.regime_labeling`에 넣을 값
5. Phase 3이 smoothed/posthoc label을 사용할 수 있는 범위
6. Phase 3이 `usable_in_hybrid`를 판단할 때 causal label만 사용할 것
7. Phase 3이 `strategy_profile.lifecycle_status = analyzed`로 전환할 조건
8. Phase 3이 Phase 4 기준을 사후 수정하지 않을 것
9. revised regime candidate를 다음 연구 사이클로 분리할 것
10. Phase 2 원본 결과 파일을 덮어쓰지 않을 것
11. Phase 3이 `edge_fragment`를 생성할 때 `regime_labeling = causal`만 hybrid 후보로 다룰 것
12. Phase 3이 `strategy_evaluation`을 작성할 때 Phase 4 prediction output을 current regime label로 쓰지 않을 것

---

# 32. revised regime candidate 정책

Phase 4는 canonical regime 기준을 먼저 고정한다.

추가 regime 후보가 필요하면 다음처럼 처리한다.

1. `canonical_regime`은 그대로 둔다.
2. 새 후보는 `experimental_regime_candidate`로 문서화한다.
3. Phase 3 본 분석에는 canonical regime을 사용한다.
4. 새 후보는 별도 연구 사이클에서 검증한다.
5. 기존 Phase 3 결과에 소급 적용하지 않는다.
6. 백테스트 성과에 맞춰 regime 기준을 사후 변경하지 않는다.

예시 후보:

- `low_volatility_compression`
- `volume_expansion`
- `post_spike_reversal`
- `liquidity_stress`
- `funding_extreme`
- `open_interest_expansion`

이 후보들은 Phase 4의 supplement로 기록할 수 있지만, SPEC의 primary regime vocabulary를 임의로 대체하지 않는다.

---

# 33. 검증 테스트

Phase 4는 다음 테스트 계획을 작성하거나 가능하면 실행한다.

## 33.1 framework selection validation

1. candidate framework가 theory basis를 갖는지 검증
2. candidate framework가 SPEC canonical regime으로 mapping 가능한지 검증
3. candidate framework가 causal implementation 가능한지 검증
4. selected primary framework가 하나인지 검증
5. rejected framework 사유가 문서화되었는지 검증
6. 임의 혼합이 없는지 검증

## 33.2 classifier unit tests

선택된 primary framework 기준으로 작성한다.

SPEC-aligned trend-strength framework를 선택한 경우 필수 테스트:

1. EMA 정렬 기반 strong_up 테스트
2. EMA 정렬 기반 strong_down 테스트
3. ADX high + EMA 미정렬 transition 테스트
4. ADX low + high volatility volatile 테스트
5. ADX low + normal volatility range 테스트
6. NaN warmup 처리 테스트
7. threshold boundary 테스트

## 33.3 causality tests

1. 데이터 slice를 t까지 잘랐을 때 `regime[t]`가 동일해야 한다.
2. t 이후 데이터를 붙여도 `regime[t]`가 변하면 안 된다.
3. `usable_from_timestamp`가 `timestamp`보다 이전이면 안 된다.
4. centered rolling window를 사용하면 실패 처리한다.
5. smoothed/posthoc label은 causal 파일에 섞이면 안 된다.
6. `llm_discretion_used`가 true인 label이 있으면 실패 처리한다.

## 33.4 Phase 3 join tests

1. trade entry 이전에 사용 가능했던 가장 최근 causal regime만 join한다.
2. exit regime도 exit 이전에 사용 가능했던 label만 사용한다.
3. holding path는 보유 기간 내 label만 포함한다.
4. entry 이전 label이 없으면 `unknown_or_warmup`으로 처리하거나 해당 trade를 분석 제외한다.
5. Phase 2 원본 파일은 수정하지 않는다.

---

# 34. look-ahead bias prevention checklist

다음 체크리스트를 작성하고 통과 여부를 기록한다.

| check | passed | evidence | failure_action |
|---|---|---|---|
| feature uses bars <= t only |  |  |  |
| current close feature uses next bar usable_from |  |  |  |
| no future return in current feature |  |  |  |
| no future high/low/min/max in current feature |  |  |  |
| label separated from feature |  |  |  |
| selected framework is theory-grounded |  |  |  |
| single primary framework selected |  |  |  |
| no arbitrary framework mixing |  |  |  |
| rejected frameworks documented |  |  |  |
| scaler fit train only, if used |  |  |  |
| threshold fit train only, if adaptive |  |  |  |
| clustering fit train only, if used |  |  |  |
| no Phase 2 result used |  |  |  |
| no Phase 3 result used |  |  |  |
| causal labels separated from smoothed/posthoc |  |  |  |
| Phase 2 artifacts not modified |  |  |  |
| regime_labels.csv has no strategy performance columns |  |  |  |
| llm_discretion_used is false for all labels |  |  |  |

하나라도 false이면 Phase 4 완료로 보고하지 않는다.

---

# 35. final report

Phase 4 완료 후 다음 형식으로 보고한다.

## 35.1 수행 요약

- symbol:
- timeframe:
- data period:
- primary objective: current market regime classification
- secondary objective: future regime prediction research, optional
- Stage A current classification status:
- Stage B prediction research status:
- selected primary framework:
- primary regime set:
- primary labeling method:
- Phase 2 results used: false
- Phase 3 results used: false
- Phase 4 output intended consumer: Phase 3 only
- causal classifier completed:
- regime_labels.csv generated:
- Phase 3 usage contract completed:
- look-ahead checklist passed:
- prediction research completed:
- prediction research skipped reason:
- git_commit:

## 35.2 framework 조사 요약

| framework | theory_basis | data_required | causal_possible | spec_alignment | selected | reason |
|---|---|---|---|---|---|---|

## 35.3 framework selection matrix 요약

| criterion | weight | selected_framework_score | next_best_score | notes |
|---|---:|---:|---:|---|

## 35.4 선택한 primary framework

| item | value |
|---|---|
| selected framework |  |
| theoretical basis |  |
| why fit for ETH/USDT 5m |  |
| why fit for Phase 3 |  |
| why not mixed |  |
| rejected alternatives |  |

## 35.5 regime definition summary

| regime | definition | primary framework rule | core features | expected behavior | notes |
|---|---|---|---|---|---|

## 35.6 feature catalog summary

| category | feature_count | high_priority_features | selected_features | lookahead_risks |
|---|---:|---|---|---|

## 35.7 labeling pipeline summary

| item | rule |
|---|---|
| timestamp meaning |  |
| usable_from_timestamp |  |
| causal label file |  |
| smoothed/posthoc separation |  |
| Phase 3 join key |  |
| LLM discretion | false |

## 35.8 prediction research summary

| model_type | recommended_model | target | horizon | validation | status |
|---|---|---|---|---|---|

## 35.9 look-ahead validation

| check | passed | evidence |
|---|---|---|

## 35.10 Phase 4 완료 판단

Phase 4 완료 여부는 Stage A 기준으로 판단한다.

| completion_item | passed | evidence |
|---|---|---|
| theory-based framework research completed |  |  |
| primary framework selected |  |  |
| no arbitrary mixing confirmed |  |  |
| market_regime_definition completed |  |  |
| causal_regime_classifier_spec completed |  |  |
| feature_catalog completed |  |  |
| regime_labeling_pipeline completed |  |  |
| usable_from_timestamp rule completed |  |  |
| Phase 3 usage contract completed |  |  |
| look-ahead checklist passed |  |  |
| Phase 2 results not used |  |  |
| Phase 3 results not used |  |  |

Stage B prediction research는 추가 연구이므로 완료 여부를 별도로 보고하되 Phase 4 핵심 완료 조건으로 삼지 않는다.

## 35.11 Phase 3 handoff

- Phase 3 should read:
- Phase 3 should generate:
- Phase 3 must not modify:
- Phase 3 must use only causal labels for hybrid eligibility:
- Phase 3 should treat smoothed/posthoc labels as analysis-only:
- Phase 3 should create `edge_fragment`:
- Phase 3 should create `strategy_evaluation`:
- Phase 3 should transition `strategy_profile.lifecycle_status` to `analyzed` only after analysis:

## 35.12 한계와 다음 연구

- optional data missing:
- selected framework limitations:
- threshold limitations:
- regime ambiguity:
- revised regime candidates:
- prediction model limitations:
- next validation tasks:

---

# 36. 절대 금지

다음은 절대 금지한다.

1. Phase 2 백테스트 결과를 Phase 4 regime 정의에 사용
2. Phase 3 분석 결과를 Phase 4 regime 정의에 사용
3. 미래 수익률을 현재 regime feature로 사용
4. future high/low/min/max를 현재 feature로 사용
5. test set 성과로 threshold 조정
6. 전체 데이터로 scaler fit
7. 전체 데이터로 clustering fit
8. posthoc label을 causal처럼 표시
9. smoothed label을 hybrid 채용 근거로 사용
10. `usable_in_hybrid` 계산
11. `edge_fragment` 생성
12. `strategy_evaluation` 생성
13. `strategy_profile.lifecycle_status` 업데이트
14. Phase 2 결과 파일 수정
15. Phase 2 `trades.csv`에 regime 컬럼 추가
16. Phase 2 `signals.csv`에 regime 컬럼 추가
17. 선택 데이터가 없는데 있는 것처럼 feature 생성
18. 예측 모델 정확도를 과장
19. 예측 결과를 확정적 미래처럼 표현
20. 현재 시장 상황 분류가 완료되기 전에 미래 시장 예측 연구를 시작
21. prediction model을 current regime classifier보다 우선
22. prediction output을 현재 regime label처럼 사용
23. prediction 연구 미완료를 이유로 Stage A 완료 산출물을 지연
24. 미래 예측 성능을 근거로 current regime threshold 조정
25. future label을 current regime feature에 섞기
26. Phase 4 최종 보고에서 예측 연구를 핵심 성과처럼 과장
27. LLM의 주관적 판단으로 regime 정의
28. 여러 framework를 임의 혼합
29. 성과가 좋아 보이도록 framework 선택 또는 threshold 선택
30. 사용자에게 중간 질문하고 작업 중단

---

# 37. 작업 순서

이제 Phase 4를 수행하라.

작업은 반드시 Stage A와 Stage B로 나누어 수행한다.

## 37.1 Stage A: 현재 시장 상황 분류 연구

먼저 현재 시장 상황 분류를 완료한다.

순서:

1. 작업 브랜치를 생성한다.
2. `services/backtest/research_store/SPEC.md`를 읽는다.
3. 기존 regime 관련 코드를 읽는다.
4. Phase 4가 Phase 2 결과를 사용하지 않는 독립 연구임을 확인한다.
5. 데이터 경로와 OHLCV/funding/open interest 등 입력 가능성을 확인한다.
6. 데이터 품질 점검을 수행한다.
7. theory-based candidate regime framework들을 조사한다.
8. `regime_framework_research.md`를 작성한다.
9. `regime_framework_selection_matrix.csv`를 작성한다.
10. 하나의 primary framework를 선택한다.
11. 선택 사유와 탈락 사유를 문서화한다.
12. 임의 framework 혼합이 없음을 검증한다.
13. selected primary framework와 SPEC canonical regime의 mapping을 문서화한다.
14. canonical regime definition을 문서화한다.
15. 현재 시장 상황 분류에 사용할 feature catalog를 작성한다.
16. causal feature timing과 `usable_from_timestamp` 규칙을 정의한다.
17. causal regime classifier spec을 작성한다.
18. 기존 classifier 구현과 SPEC의 불일치를 확인한다.
19. causal regime labeling pipeline을 설계한다.
20. 데이터가 있으면 causal `regime_labels.csv`를 생성한다.
21. smoothed/posthoc label은 필요 시 별도 파일로 분리한다.
22. Phase 3 trade join rule을 작성한다.
23. Phase 3 usage contract를 작성한다.
24. look-ahead checklist를 작성하고 검증한다.
25. Stage A 완료 여부를 판단한다.

Stage A 완료 조건:

1. `regime_framework_research.md` 작성 완료
2. `regime_framework_selection_matrix.csv` 작성 완료
3. `selected_primary_regime_framework.md` 작성 완료
4. `market_regime_definition.md` 작성 완료
5. `causal_regime_classifier_spec.md` 작성 완료
6. `regime_feature_catalog.csv` 작성 완료
7. `regime_labeling_pipeline_spec.md` 작성 완료
8. `regime_labels_schema.md` 작성 완료
9. `phase3_usage_contract.md` 작성 완료
10. `lookahead_bias_prevention_checklist.md` 통과
11. Phase 2 결과를 사용하지 않았음
12. Phase 3 결과를 사용하지 않았음
13. Phase 4 결과가 Phase 2에서 사용되지 않도록 명시함
14. LLM discretionary regime definition을 사용하지 않았음
15. arbitrary framework mixing이 없었음

위 조건 중 하나라도 미완성이면 Stage B로 넘어가지 마라.

## 37.2 Stage B: 미래 시장 상황 예측 추가 연구

Stage A가 완료된 경우에만 진행한다.

순서:

1. future regime prediction이 Stage A의 부가 연구임을 명시한다.
2. prediction horizon을 정의한다.
3. prediction target label을 정의한다.
4. label과 feature 시점을 분리한다.
5. rule-based transition model을 검토한다.
6. statistical model 후보를 검토한다.
7. ML model 후보를 검토한다.
8. time split 또는 walk-forward validation 계획을 작성한다.
9. look-ahead bias 방지 규칙을 작성한다.
10. prediction 연구의 한계와 Phase 3 사용 가능 범위를 명시한다.

Stage B는 선택적이다.

Stage B가 미완료여도 Stage A가 완료되면 Phase 4의 핵심 목적은 달성된 것으로 보고할 수 있다.

중간에 사용자에게 질문하지 마라.
불확실한 경우 보수적 가정을 세우고, 그 가정과 영향을 기록하라.
DB, 파일, 데이터, 테스트 결과를 실제로 확인하지 않았으면 확인했다고 말하지 마라.
Phase 4 결과는 Phase 3에서만 사용한다고 끝까지 유지하라.


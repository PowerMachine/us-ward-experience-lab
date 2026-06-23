# Feedback Guide

Thank you for testing U.S. Ward Experience Lab.

This is a beta educational simulation for Korean RNs preparing for U.S. hospital work experience.

## Short Feedback Form

Please submit short feedback here:

```text
https://docs.google.com/forms/d/e/1FAIpQLScUc4cvKVPYf1DdItAYW74V8bXQidAS9CHh7d5akhNyv2Oe5w/viewform?usp=publish-editor
```

It should take about 1-2 minutes.

## Please do not include

- Real patient name
- Hospital name
- Date of birth
- Medical record number
- Phone number
- Address
- Photo
- Real lab result
- Any identifiable health information

## Good feedback examples

- "Provider call practice needs more realistic English."
- "Please add CNA/PCT delegation scenarios."
- "The Korean explanation feels too translated."
- "Medication room workflow was useful."
- "Please add more first-day orientation situations."

## Recommended Google Form

Title:

```text
U.S. Ward Experience Lab v0.1.0-beta Feedback
```

Description:

```text
미국 병원 취업/이민을 준비하는 한국 RN을 위한 교육용 시뮬레이션 베타 피드백입니다.
1-2분 안에 끝나는 짧은 피드백입니다.
실제 환자정보, 병원명, 환자 이름, 생년월일, MRN, 전화번호, 주소 등 식별 가능한 정보는 입력하지 말아주세요.
```

Questions:

1. 현재 상태는 무엇인가요?  
   Type: multiple choice, required  
   Choices: NCLEX 준비 중 / NCLEX 합격 / VisaScreen 또는 이민 준비 중 / 미국 취업 준비 중 / 한국 현직 RN / 미국 현직 RN / 기타

2. 어떤 기능을 사용해보셨나요?  
   Type: checkbox, required  
   Choices: 첫 7일 / 병동 투어 / 스테이션 실습 / 환자 케이스 / SBAR / 직무 트랙 / 전체적으로 둘러봄

3. 미국 병동 분위기를 이해하는 데 도움이 되었나요?  
   Type: linear scale, required  
   1 = 전혀 도움 안 됨, 5 = 매우 도움 됨

4. 미국 병동 상황처럼 현실감이 있었나요?  
   Type: linear scale, required  
   1 = 현실감 낮음, 5 = 현실감 높음

5. 가장 보완되었으면 하는 부분은 무엇인가요?  
   Type: multiple choice, required  
   Choices: 미국 병동 시나리오 추가 / 영어 표현 또는 SBAR 보완 / 한국어 설명 자연스럽게 수정 / 화면 디자인 또는 가독성 개선 / 실제 업무 흐름 설명 보완 / 오류 또는 버그 수정 / 잘 모르겠음 / 기타

6. AI 개발자에게 바로 전달한다면, 어떤 점을 고치라고 말하고 싶나요?  
   Type: short answer or short paragraph, required  
   Examples: provider call 상황을 더 실제처럼 만들어주세요. CNA/PCT에게 부탁하는 상황을 더 추가해주세요. 한국어 문장이 번역투라 자연스럽게 고쳐주세요.

7. 익명화된 피드백을 프로그램 개선 및 성과 증빙에 활용해도 될까요?  
   Type: multiple choice, required  
   Choices: 예 / 아니오

## Google Sheet Column Names

Use these column names when exporting feedback for AI analysis:

```text
timestamp
user_stage
tested_modules
usefulness_score
realism_score
main_improvement_area
one_line_feedback_for_ai
anonymous_use_consent
version
```

## AI Analysis Prompt

Copy the CSV contents with this prompt:

```text
너는 U.S. Ward Experience Lab의 제품 개선 PM이자 도메인 분석 보조자다.

아래는 미국 이민/취업을 준비하는 한국 RN 사용자의 베타 피드백 CSV다.

나는 간호 도메인을 잘 모르고, 피드백을 일일이 읽을 생각이 없다.

네가 할 일:

1. 피드백을 주제별로 자동 분류해라.
2. 가장 많이 나온 개선 요구 Top 10을 뽑아라.
3. 간호 도메인 관점에서 중요한 요구와 단순 취향을 구분해라.
4. 실제 미국 병동 workflow와 관련된 개선 요구를 우선순위로 올려라.
5. 다음 버전 v0.1.1-beta에 반영할 작업 목록을 만들어라.
6. Codex에게 줄 수 있는 개발 지시문으로 변환해라.
7. 개인정보나 실제 환자정보가 포함된 응답은 사용하지 말고 제외해라.

출력 형식:

# 피드백 분석 요약

## 총 응답 수
## 평균 도움 점수
## 평균 현실감 점수

## 주요 개선 요구 Top 10
| 순위 | 요구사항 | 빈도 | 중요도 | 이유 |

## 즉시 반영할 수정사항
## 다음 버전에 반영할 기능
## 보류할 요구사항
## 삭제/무시할 위험한 피드백

## Codex 작업 지시문
바로 복사해서 Codex에 넣을 수 있게 작성해라.
```

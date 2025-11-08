# 네트워크 운영 개선 자동화 프로젝트

Ansible과 Python을 활용하여 **네트워크 장비의 백업, 점검, 이력 관리 프로세스를 자동화**하고  
**HTML 리포트 및 Slack 알림**을 통해 운영 현황을 시각화한 프로젝트입니다.

---

## 1. 프로젝트 개요

|     항목     |    내용  |
|------------- |------------|
| **프로젝트명** | 네트워크 운영 개선 자동화 |
| **개발기간**  | 2025.10 ~ 2025.11 |
| **기술 스택** | Vagrant, Ansible, Python3, HTML, Slack Webhook |
| **주요 기능** | 백업 자동화, 계정 현행화, EOS/EOL 리포트, Config 변경 비교 |
| **작성자**   | 김지나 |

---

## 2. 주요 기능 요약

### 1) Config 자동 백업 
- Ansible 기반 **TFTP 서버 자동 구성**
- cron을 통해 **주기적(10분~1시간 간격)** 설정 백업 수행
  - 테스트 환경에서는 비교적 짧은 주기로 설정
- **Vault 기능**을 사용하여 장비 패스워드 파일 암호화 
- cron 동작 시 **자동 백업 실행 로그(`backup.log`)** 기록
- 장비별 폴더를 생성하고, `호스트명-YYYYMMDD-HHMM.cfg` 형식으로 파일 관리
  - 날짜뿐 아니라 시간 단위로 구분하여 변경 시점을 명확히 확인 가능

### 2) 계정 현행화 자동화
- YAML 파일 내 정의된 사용자 목록(`valid_users`) 기준으로 계정 동기화 

### 3) EOS/EOL 점검 리포트
- 장비의 **호스트명, 모델명, OS 버전, 시리얼** 정보 자동 수집
- CSV 파일(`nxosv_eos_list.csv`)과 비교하여 **EOS/EOL 상태 자동 판별**
- **EOS/EOL 점검 HTML 리포트** 자동 생성
- `serve_utf8.py` 내장 웹서버 실행 후 
  **웹 브라우저에서 깨짐 없이 리포트 열람 가능**

### 4) Config 변경 비교 및 Slack 알림
- **전날 대비 Config 변경 비교**(`difflib.HtmlDiff` 모듈 활용)
- 변경 발생 시 **Slack Webhook**으로 알림 발송  
- `!Time`, `!Command` 등 **변경과 무관한 문자열**은 자동 필터링
- **Config 비교 결과 HTML 리포트** 자동 생성
- `serve_utf8.py` 내장 웹서버 실행 후 
  **웹 브라우저에서 깨짐 없이 리포트 열람 가능**
  
---

## 3. 프로젝트 구조
```bash 

/home/vagrant
 ├── tftp_backup/            # 장비별 설정 백업 저장 경로
 │        
 ├── .vault_pass.txt         # Ansible Vault 패스워드 파일
 │
 └── ansible_project/
     ├── playbooks/                       # Ansible 자동화 스크립트
     │   ├── tftp_setup.yml               # TFTP 서버 구축
     │   ├── collect_config.yml           # 수동 백업 (ask-vault-pass 사용)
     │   ├── backup_config.yml            # 자동 백업 (cron, vault-pass 파일 사용)
     │   ├── delete_users.yml             # 지정 사용자 삭제
     │   ├── sync_users.yml               # 운영자 계정 자동 동기화 (삭제/생성)
     │   └── collect_device_details.yml   # 장비 상세 정보 수집
     │   
     ├── inventory/                   # 대상 장비 
     │   ├── hosts.ini                # 장비 접속 정보 
     │   └── host_vars/               # 장비별 암호화 패스워드 파일
     │   
     ├── data/                        # EOS/EOL 데이터 파일     
     │   
     ├── scripts/                     # Python 비교 스크립트
     │   
     ├── docs/                        # 프로젝트 문서 (plan.md 등)
     │
	 ├── reports/                     # 자동 생성 리포트 (HTML, JSON)
     │
	 ├── backup.log         # cron 실행 시 Ansible 결과 로그
     ├── ansible.cfg        # Ansible 환경 설정
     └── serve_utf8.py      # UTF-8 웹서버 (리포트 확인용)

	 
**자동 생성 항목**
- tftp_backup/ : 장비명 폴더별 백업 파일 자동 생성
- reports/ : HTML, JSON 리포트 자동 생성
- backup.log : 자동 백업 실행 로그 기록

```

---

## 4. 설치 환경

- **VirtualBox** : 7.1.10
- **Vagrant** : 2.4.7
- **Ansible-Server** : Ubuntu 18.04 *(Vagrantfile 실행 시 자동 설치)*
- **Ansible** : 2.9.27
- **Python** : 2.7.17 -> 3.6.9 *(Ansible JSON 파싱 호환성 문제로 업그레이드)*
- **NXOSv** : nxosv-final.7.0.3.I7.9.vmdk *(Cisco 공식 다운로드)*
- **브라우저** : Chrome / Whale *(HTML 리포트 확인용)*

---

## 5. 실행 방법

### 1) 테스트 환경 구성
1. VirtualBox 설치
2. Vagrant 설치 
3. Vagrantfile 실행 -> Ansible-Server 자동 생성
4. Ansible-Server에 Python3 설치 
5. NXOSv 이미지 추가 후 네트워크 연결
 *(Ansible-Server와 NXOSv는 동일 네트워크 대역으로 설정)*

--- 

### 2) 실행 절차 (Path: `/home/vagrant/ansible_project`)

#### Config 백업
```bash
ansible-playbook playbooks/tftp_setup.yml
ansible-playbook playbooks/collect_config.yml --ask-vault-pass
ansible-playbook playbooks/backup_config.yml
```

#### 계정 현행화
```bash
ansible-playbook playbooks/delete_users.yml --ask-vault-pass
ansible-playbook playbooks/sync_users.yml --ask-vault-pass
```

#### EOS/EOL 리포트
```bash 
ansible-playbook playbooks/collect_device_details.yml --ask-vault-pass
python3 scripts/compare_eos.py
python3 scripts/serve_utf8.py
# 브라우저 접속: http://<Ansible-Server IP>:8080/reports/eos_report.html
```

#### Config 변경 비교
```bash
python3 scripts/compare_config_diff.py
python3 scripts/serve_utf8.py
# 브라우저 접속: http://<Ansible-Server IP>:8080/reports/nxosv-test01_config_diff.html
```

---

### 추가 설정
- `.vault_pass.txt` : Vault 패스워드 파일 생성
- `ansible.cfg` : inventory, vault_password_file 경로 지정
- `hosts.ini` : 관리 대상 정보(그룹명, 호스트명, IP, 계정, 연결 방식 등)
- `host_vars/<호스트명>.yml` : 장비의 암호화된 패스워드
- `/etc/cron.d/nxos_backup` : 자동 백업 crontab 설정

---

## 6. 실행 결과 (결과 증빙)

모든 캡처 이미지는 실제 Ansible 플레이북 실행 및 Python 리포트 결과를 기반으로 생성되었습니다.  

| 구분 |  이미지 경로 |
|------|--------------|
| EOS/EOL 리포트 | `docs/images/eos_report_example.png` |
| Config 변경 비교 | `docs/images/config_diff_example.png` |
| Slack 알림 | `docs/images/slack_alert_example.png` |

---

## 7. 개선 방향 

프로젝트 완료 후, 보안성과 확장성을 중심으로 아래와 같이 확장 계획을 수립하였습니다.

- TFTP -> SFTP 전환으로 보안 강화
- CSV 기반 백업 대상 자동 관리 기능 추가
- 주기적 백업 압축 및 오래된 파일 자동 삭제 기능 추가
- 백업 실패 시 Slack 알림 전송
- EOS/EOL 리포트 HTML, CSV 동시 출력 기능 추가 
- Cisco 공식 API 연동을 통한 EOS/EOL 정보 자동 수집 
- ISMS/KISA 대비 보안 설정 점검 자동화
- 공통 설정 자동 반영(SNMP 등)으로 운영 표준화 

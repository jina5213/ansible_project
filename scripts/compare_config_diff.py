import difflib, os, requests, re

# 환경 설정
BACKUP_ROOT = "../tftp_backup"
REPORT_DIR = "reports"
SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK_URL")


# 무시할 줄 패턴 정의
ignore_patterns = [
    r'^\s*!Command:',
    r'^\s*!Time:',
    r'^\s*!No configuration',
    r'^\s*!Running configuration',
]

# 비교가 불필요한 line 제거하고 공백/줄바꿈 정리 함수 정의
def line_trim(lines):
    out = []
    for line in lines:
        # 패턴 중 하나라도 매칭되면 무시
        if any(re.search(p, line) for p in ignore_patterns):
            continue
        # 공백/줄바꿈 제거하고 리스트에 추가
        out.append(line.strip())
    return out


# 장비 별 폴더 순회 
for device in os.listdir(BACKUP_ROOT):
    device_path = os.path.join(BACKUP_ROOT, device)
    if not os.path.isdir(device_path):
        continue    # 폴더 아니면 skip, 폴더만 처리
    
    # 장비 별 반복, 백업 파일 리스트 가져오기
    files = sorted([f for f in os.listdir(device_path) if f.endswith(".cfg")])
    if len(files) < 2:
        print(f"{device}: 비교할 파일 개수 부족!.")
        continue
        
    old_file = os.path.join(device_path, files[-2])
    new_file = os.path.join(device_path, files[-1])
    output_file = os.path.join(REPORT_DIR, f"{device}_config_diff.html")
    
    # 백업 파일 읽기
    with open(old_file, 'r', encoding='utf-8', errors='ignore') as f1, \
         open(new_file, 'r', encoding='utf-8', errors='ignore') as f2:
        old_raw = f1.readlines()
        new_raw = f2.readlines()

    # 불필요한 줄 제거
    old_data = line_trim(old_raw)
    new_data = line_trim(new_raw)
    
    # 컨피그 line 개수 확인
    print(f"Old lines: {len(old_data)}")
    print(f"New lines: {len(new_data)}")

  
    # 백업 파일 diff 확인
    diff = difflib.HtmlDiff(wrapcolumn=80).make_file(
           old_data, new_data, 
           fromdesc=f"Old_config: {files[-2]}", 
           todesc=f"New_config: {files[-1]}"
    )           

    # 결과 저장
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("<!DOCTYPE html>\n")     
        f.write("<html>\n<head>\n<meta charset='utf-8'>\n</head>\n<body>\n")   
        f.write(f"<h2>{device} Config 변경 비교 결과</h2>\n")
        f.write(diff)
        f.write("\n</body></html>")

    print(f"{device}: Diff 결과 생성 완료 → {output_file}")
    
    
    # slack 알림
    if old_data != new_data:
        message = {
            "text": f"[{device}] ⚠️설정 변경 감지!\n"
                    f"비교 파일: {files[-2]} & {files[-1]}\n"
                    f"결과 파일: {output_file}"
        }
        try:
            requests.post(SLACK_WEBHOOK, json=message)
            print(f"{device}: Slack 알림 전송 완료")
        except Exception as e:
            print(f"{device}: Slack 알림 전송 실패 ({e})")
    else:
        print(f"{device}: 변경 없음")
    
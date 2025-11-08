import json, csv, os
from datetime import datetime

# 디렉토리 경로 
REPORT_DIR = "reports"
DATA_FILE = "data/nxosv_eos_list.csv"

# csv 파일 읽기
with open(DATA_FILE, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    eos_data = list(reader)

# HTML 리포트 파일 경로 지정
output_path = os.path.join(REPORT_DIR, "eos_report.html")

# HTML 구문
html = []
html.append("<h2> 네트워크 EOS/EOL 점검 리포트</h2>")
html.append(
     "<table border=1><tr>"
     "<th>Hostname</th><th>Model</th>"
     "<th>Serial</th><th>Version</th><th>Status</th>"
     "</tr>"
)

# JSON 파일 읽기 (_info.json 파일 불러와서 딕셔너리 형태로 읽음)
for file in os.listdir(REPORT_DIR):
    if file.endswith("_info.json"):
        with open(os.path.join(REPORT_DIR, file), 'r', encoding='utf-8') as jf:
            device = json.load(jf)

        hostname = device["hostname"]
        model = device["model"]
        serial = device["serial"]
        version = device["version"]
        
# eos_data: csv 파일, device[] : json 파일        
        status = "모델 미등록"
        for row in eos_data:
            if row["Model"].lower() in model.lower():
                eos = datetime.strptime(row["EOS Date"], "%Y-%m-%d")
                eol = datetime.strptime(row["EOL Date"], "%Y-%m-%d")
                today = datetime.today()
                
                if today > eol:
                    status = "❌EOL(지원 종료)"
                elif today > eos:
                    status = "⚠️EOS(판매 종료)"
                else:
                    status = "✅판매 중"
                break
        
        html.append( 
            "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td>"
            "<td>{}</td></tr>".format(
               hostname, model, serial, version, status
            )
        )
 
html.append("</table>")


# 결과 파일 저장
with open(output_path, "w", encoding='utf-8') as f:
    
 # HTML5 표준 규칙으로 렌더링 
    f.write("<!DOCTYPE html>\n")    
    
 # 문서 자체 인코딩 명시
    f.write("<html>\n<head>\n<meta charset='utf-8'>\n</head>\n<body>\n")   
    f.write("\n".join(html))
    f.write("\n</body>\n</html>")

print("Report created: %s" % output_path) 

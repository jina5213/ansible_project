# python3 -m http.server 실행 시 내부적으로 사용하는 클래스
from http.server import SimpleHTTPRequestHandler, HTTPServer

# 클래스 상속받아 응답헤더 끝나기 전에 charset=utf-8 강제 추가
class UTF8Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Content-Type", "text/html; charset=utf-8")
        super().end_headers()

# 서버 객체(httpd) 생성
server_address = ("0.0.0.0", 8080)
httpd = HTTPServer(server_address, UTF8Handler)
print("Serving on http://0.0.0.0:8080")
httpd.serve_forever()

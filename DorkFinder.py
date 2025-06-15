import socket
import select
import struct
from socketserver import ThreadingMixIn, TCPServer, StreamRequestHandler

class Socks5Proxy(StreamRequestHandler):
    def handle(self):
        try:
            # مرحله ۱: احراز هویت (Authentication)
            self.connection.recv(1024)  # دریافت نسخه و متدهای احراز هویت
            self.connection.sendall(b"\x05\x00")  # پاسخ: نیازی به احراز هویت نیست

            # مرحله ۲: دریافت درخواست اتصال
            data = self.connection.recv(1024)
            if len(data) < 7:
                raise Exception("درخواست نامعتبر")

            version, cmd, _, addr_type = struct.unpack("!BBBB", data[:4])
            if version != 5 or cmd != 1:  # فقط از اتصال (CMD=1) پشتیبانی می‌شود
                self.connection.sendall(b"\x05\x07\x00\x01\x00\x00\x00\x00\x00\x00")  # پاسخ خطا
                return

            # استخراج آدرس مقصد
            if addr_type == 1:  # IPv4
                remote_addr = socket.inet_ntoa(data[4:8])
                remote_port = struct.unpack("!H", data[8:10])[0]
            elif addr_type == 3:  # Domain Name
                domain_length = data[4]
                remote_addr = data[5:5+domain_length].decode()
                remote_port = struct.unpack("!H", data[5+domain_length:7+domain_length])[0]
            else:
                raise Exception("نوع آدرس پشتیبانی نمی‌شود")

            # اتصال به مقصد
            remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote.connect((remote_addr, remote_port))
            
            # پاسخ موفقیت‌آمیز به کلاینت
            self.connection.sendall(b"\x05\x00\x00\x01\x00\x00\x00\x00\x00\x00")

            # انتقال داده بین کلاینت و مقصد
            while True:
                r, _, _ = select.select([self.connection, remote], [], [])
                if self.connection in r:
                    data = self.connection.recv(4096)
                    if not data:
                        break
                    remote.sendall(data)
                if remote in r:
                    data = remote.recv(4096)
                    if not data:
                        break
                    self.connection.sendall(data)

        except Exception as e:
            print(f"خطا: {e}")
        finally:
            remote.close() if 'remote' in locals() else None

class ThreadingTCPServer(ThreadingMixIn, TCPServer):
    pass

if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 1080
    with ThreadingTCPServer((HOST, PORT), Socks5Proxy) as server:
        print(f"سرور SOCKS5 در حال اجرا روی پورت {PORT}...")
        server.serve_forever()

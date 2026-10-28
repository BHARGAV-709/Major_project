import socket
import struct
import json
import urllib.request
import base64
import os
import time

class SimpleCDPClient:
    def __init__(self, page_id=None):
        if not page_id:
            with urllib.request.urlopen("http://127.0.0.1:9222/json") as r:
                pages = json.loads(r.read().decode())
                for p in pages:
                    if "3000" in p.get("url", "") or "Dashboard" in p.get("title", ""):
                        page_id = p["id"]
                        break
                if not page_id:
                    page_id = pages[0]["id"]
        self.page_id = page_id
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(("127.0.0.1", 9222))
        self._handshake()
        self.cmd_id = 0

    def _handshake(self):
        key = base64.b64encode(os.urandom(16)).decode()
        req = (
            f"GET /devtools/page/{self.page_id} HTTP/1.1\r\n"
            f"Host: 127.0.0.1:9222\r\n"
            f"Upgrade: websocket\r\n"
            f"Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            f"Sec-WebSocket-Version: 13\r\n\r\n"
        )
        self.sock.sendall(req.encode())
        res = self.sock.recv(4096)
        assert b"101 " in res, f"Handshake failed: {res.decode()}"

    def _send_frame(self, text):
        data = text.encode("utf-8")
        length = len(data)
        mask = os.urandom(4)
        masked_data = bytearray(b ^ mask[i % 4] for i, b in enumerate(data))
        if length <= 125:
            header = bytes([0x81, 0x80 | length]) + mask
        elif length <= 65535:
            header = bytes([0x81, 0xFE]) + struct.pack("!H", length) + mask
        else:
            header = bytes([0x81, 0xFF]) + struct.pack("!Q", length) + mask
        self.sock.sendall(header + masked_data)

    def _recv_frame(self):
        header = self.sock.recv(2)
        if not header:
            return None
        byte1, byte2 = header[0], header[1]
        length = byte2 & 0x7F
        if length == 126:
            length = struct.unpack("!H", self.sock.recv(2))[0]
        elif length == 127:
            length = struct.unpack("!Q", self.sock.recv(8))[0]
        
        payload = bytearray()
        while len(payload) < length:
            chunk = self.sock.recv(min(length - len(payload), 65536))
            if not chunk:
                break
            payload.extend(chunk)
        return payload.decode("utf-8", errors="replace")

    def execute(self, method, params=None, timeout=10):
        self.cmd_id += 1
        req_id = self.cmd_id
        msg = json.dumps({"id": req_id, "method": method, "params": params or {}})
        self._send_frame(msg)

        start = time.time()
        while time.time() - start < timeout:
            frame = self._recv_frame()
            if not frame:
                continue
            try:
                res = json.loads(frame)
                if res.get("id") == req_id:
                    return res
            except Exception:
                pass
        return None

    def evaluate(self, expression):
        res = self.execute("Runtime.evaluate", {"expression": expression, "returnByValue": True})
        if res and "result" in res and "result" in res["result"]:
            return res["result"]["result"].get("value")
        return None

    def capture_screenshot(self, filepath):
        res = self.execute("Page.captureScreenshot", {"format": "png"})
        if res and "result" in res and "data" in res["result"]:
            with open(filepath, "wb") as f:
                f.write(base64.b64decode(res["result"]["data"]))
            return True
        return False

    def navigate(self, url):
        self.execute("Page.navigate", {"url": url})
        time.sleep(1.5)

    def close(self):
        try:
            self.sock.close()
        except:
            pass

if __name__ == "__main__":
    client = SimpleCDPClient()
    print("CDP connected to page!")
    title = client.evaluate("document.title")
    print("Page Title:", title)
    client.capture_screenshot("page_screenshot.png")
    print("Screenshot saved to page_screenshot.png")
    client.close()

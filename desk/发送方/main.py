import socket
import pyautogui
from PIL import Image
import io
import struct
import time
def capture_screen():
    screen = pyautogui.screenshot()
    screen_bytes = io.BytesIO()
    screen.save(screen_bytes, format='JPEG')
    return screen_bytes.getvalue()

def send_screen_to_client(conn):
    screen_data = capture_screen()
    conn.sendall(struct.pack('>I', len(screen_data)))
    conn.sendall(screen_data)

def main():
    host = '192.168.31.26'  # 电脑A的IP地址
    port = 34566

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print("Listening for client connections...")
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            try:
                while True:
                    send_screen_to_client(conn)
            except ConnectionResetError:
                print("Connection closed by client.")

if __name__ == '__main__':
    while True:
        try:
            main()
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
            continue


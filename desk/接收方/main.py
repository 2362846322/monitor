import socket
import struct
import cv2
import numpy as np
import io

def receive_screen_from_server(conn):
    raw_msglen = recvall(conn, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    screen_data = recvall(conn, msglen)
    screen_array = np.frombuffer(io.BytesIO(screen_data).getbuffer(), dtype=np.uint8)
    screen = cv2.imdecode(screen_array, cv2.IMREAD_COLOR)
    return screen

def recvall(conn, n):
    data = bytearray()
    while len(data) < n:
        packet = conn.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data

def main():
    host = '192.168.31.120'  # 电脑A的IP地址
    port = 12345

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        try:
            cv2.namedWindow('Remote Screen', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('Remote Screen', 800, 600)
            while True:
                screen = receive_screen_from_server(s)
                if screen is not None:
                    cv2.imshow('Remote Screen', screen)
                    if cv2.waitKey(1) & 0xFF == ord('q'):  # 按'q'退出
                        break
                else:
                    break
        except ConnectionResetError:
            print("Server closed the connection.")
        finally:
            cv2.destroyAllWindows()

if __name__ == '__main__':
    main()

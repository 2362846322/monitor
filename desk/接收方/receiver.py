import socket
import struct
import cv2
import numpy as np
import io
import screeninfo


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


def get_local_screen_resolution():
    screen = screeninfo.get_monitors()[0]
    return screen.width, screen.height


def main():
    host = '192.168.31.161'  # 电脑A的IP地址
    port = 12345

    screen_width, screen_height = get_local_screen_resolution()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        try:
            cv2.namedWindow('Remote Screen', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('Remote Screen', screen_width, screen_height)

            while True:
                screen = receive_screen_from_server(s)
                if screen is not None:
                    # 保持图像比例缩放
                    h, w, _ = screen.shape
                    aspect_ratio = w / h
                    new_width = screen_width
                    new_height = int(screen_width / aspect_ratio)
                    if new_height > screen_height:
                        new_height = screen_height
                        new_width = int(screen_height * aspect_ratio)
                    screen_resized = cv2.resize(screen, (new_width, new_height))
                    # 将图像居中显示
                    top_padding = (screen_height - new_height) // 2
                    bottom_padding = screen_height - new_height - top_padding
                    left_padding = (screen_width - new_width) // 2
                    right_padding = screen_width - new_width - left_padding
                    screen_padded = cv2.copyMakeBorder(screen_resized, top_padding, bottom_padding, left_padding,
                                                       right_padding, cv2.BORDER_CONSTANT)
                    cv2.imshow('Remote Screen', screen_padded)

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                else:
                    break
        except ConnectionResetError:
            print("Server closed the connection.")
        finally:
            cv2.destroyAllWindows()


if __name__ == '__main__':
    main()

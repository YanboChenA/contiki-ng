import socket

# 服务器的IP地址和端口
SERVER_IP = "0.0.0.0"  # 监听所有可用的接口
SERVER_PORT = 1234     # 确保这个端口与Cooja仿真中的Socket Client设置匹配

# 创建一个TCP/IP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 防止socket.close()后端口被占用
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# 绑定socket到端口
server_socket.bind((SERVER_IP, SERVER_PORT))

# 监听传入连接
server_socket.listen(1)

print(f"Server is listening on {SERVER_IP}:{SERVER_PORT}")

try:
    while True:
        # 等待客户端连接
        print("Waiting for a connection...")
        connection, client_address = server_socket.accept()
        print(f"Connected by {client_address}")

        while True:
            data = connection.recv(1024)
            if not data:
                break  # 客户端已断开连接
            print(f"Received: {data.decode()}")

            if data.decode().strip() == "success":
                print("Success message received. Closing connection.")
                break

        connection.close()

except KeyboardInterrupt:
    print("Server is shutting down.")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # 关闭socket
    server_socket.close()

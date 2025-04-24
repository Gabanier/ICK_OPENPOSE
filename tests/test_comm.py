import socket

def main(args=None):

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(("127.0.0.1", 7777))
    print("Server is listening for incomming messages")

    message_counter = 0

    while True:
        try:
            data, addr = server_socket.recvfrom(5)
        except KeyboardInterrupt:
            print(f"Received {message_counter} messages")
            return
        message_counter += 1
        print(f"Received from: {addr} message: {data.decode()}")


if __name__ == "__main__":
    main()
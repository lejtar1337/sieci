#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

void error_exit(const char *msg) {
    perror(msg);
    exit(EXIT_FAILURE);
}

int main(int argc, char *argv[]) {
    if (getuid() == 0) {
        fprintf(stderr, "Błąd: Uruchamianie z konta root jest zablokowane.\n");
        exit(EXIT_FAILURE);
    }

    int port = (argc > 1) ? atoi(argv[1]) : 80;

    int server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd < 0) error_exit("socket");

    int opt = 1;
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)) < 0)
        error_exit("setsockopt");

    struct sockaddr_in addr;
    memset((char*)&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_ANY);
    addr.sin_port = htons(port);

    if (bind(server_fd, (struct sockaddr*)&addr, sizeof(addr)) < 0)
        error_exit("bind");

    if (listen(server_fd, 5) < 0)
        error_exit("listen");

    while (1) {
        int client_fd = accept(server_fd, NULL, NULL);
        if (client_fd < 0) {
            perror("accept");
            continue;
        }

        char buffer[1024];
        if (recv(client_fd, buffer, sizeof(buffer) - 1, 0) < 0) {
            perror("recv");
            close(client_fd);
            continue;
        }

        FILE *f = fopen("/proc/uptime", "r");
        char uptime[64] = "Brak danych";
        if (f) {
            fscanf(f, "%s", uptime);
            fclose(f);
        }

        char body[128];
        snprintf(body, sizeof(body), "%s\n", uptime);

        char response[512];
        snprintf(response, sizeof(response),
                 "HTTP/1.0 200 OK\r\n"
                 "Content-Type: text/plain; charset=UTF-8\r\n"
                 "Connection: close\r\n"
                 "Content-Length: %zu\r\n\r\n"
                 "%s", strlen(body), body);

        if (send(client_fd, response, strlen(response), 0) < 0)
            perror("send");

        if (shutdown(client_fd, SHUT_WR) < 0)
            perror("shutdown");

        if (close(client_fd) < 0)
            perror("close client");
    }

    if (close(server_fd) < 0) error_exit("close server");
    return 0;
}


////sudo setcap 'cap_net_bind_service=+ep' ./server
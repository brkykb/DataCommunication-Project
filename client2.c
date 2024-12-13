#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>

#define PORT 8080
#define BUFFER_SIZE 4096

void send_image(const char *filename, int sock) {
    FILE *file = fopen(filename, "rb");
    if (!file) {
        perror("File open error");
        exit(EXIT_FAILURE);
    }

    char buffer[BUFFER_SIZE];
    size_t bytes_read;

    while ((bytes_read = fread(buffer, 1, BUFFER_SIZE, file)) > 0) {
        if (send(sock, buffer, bytes_read, 0) < 0) {
            perror("Send failed");
            fclose(file);
            close(sock);
            exit(EXIT_FAILURE);
        }
    }

    fclose(file);
    shutdown(sock, SHUT_WR);  // Veri gönderiminin tamamlandığını belirt
}

int main() {
    int sock = 0;
    struct sockaddr_in serv_addr;
    char result[BUFFER_SIZE] = {0};

    // Create socket
    if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        perror("Socket creation error");
        return -1;
    }

    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(PORT);

    if (inet_pton(AF_INET, "127.0.0.1", &serv_addr.sin_addr) <= 0) {
        perror("Invalid address");
        return -1;
    }

    // Connect to server
    if (connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0) {
        perror("Connection failed");
        return -1;
    }

    // Send image
    printf("Sending image...\n");
    send_image("deneme/paper/6.jpg", sock);

    // Receive result
    if (read(sock, result, BUFFER_SIZE) > 0) {
        printf("Server response: %s\n", result);
    } else {
        printf("Failed to receive server response\n");
    }

    close(sock);
    return 0;
}

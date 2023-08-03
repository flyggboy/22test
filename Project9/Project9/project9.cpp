#include <iostream>
#include <iomanip>
#include <cstring>
#include <openssl/aes.h>
#pragma comment(lib,"libssl.lib")
#pragma comment(lib,"libcrypto.lib")
// 打印二进制数据
void printHex(const unsigned char* data, size_t len) {
    for (size_t i = 0; i < len; ++i) {
        std::cout << std::setw(2) << std::setfill('0') << std::hex << static_cast<int>(data[i]);
    }
    std::cout << std::dec << std::endl;
}

int main() {
    // 原始数据
    unsigned char plaintext[] = "Hello, AES!";
    size_t plaintextLen = strlen((char*)plaintext);

    // 密钥
    unsigned char key[AES_BLOCK_SIZE] = "0123456789abcde"; // 注意，密钥长度需要符合AES要求

    // 初始化加密上下文
    AES_KEY aesKey;
    AES_set_encrypt_key(key, 128, &aesKey);

    // 加密
    unsigned char ciphertext[AES_BLOCK_SIZE];
    AES_encrypt(plaintext, ciphertext, &aesKey);

    // 输出加密结果
    std::cout << "Ciphertext: ";
    printHex(ciphertext, AES_BLOCK_SIZE);

    return 0;
}

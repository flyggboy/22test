#include <iostream>
#include <iomanip>
#include <cstring>
#include <openssl/aes.h>
#pragma comment(lib,"libssl.lib")
#pragma comment(lib,"libcrypto.lib")
// ��ӡ����������
void printHex(const unsigned char* data, size_t len) {
    for (size_t i = 0; i < len; ++i) {
        std::cout << std::setw(2) << std::setfill('0') << std::hex << static_cast<int>(data[i]);
    }
    std::cout << std::dec << std::endl;
}

int main() {
    // ԭʼ����
    unsigned char plaintext[] = "Hello, AES!";
    size_t plaintextLen = strlen((char*)plaintext);

    // ��Կ
    unsigned char key[AES_BLOCK_SIZE] = "0123456789abcde"; // ע�⣬��Կ������Ҫ����AESҪ��

    // ��ʼ������������
    AES_KEY aesKey;
    AES_set_encrypt_key(key, 128, &aesKey);

    // ����
    unsigned char ciphertext[AES_BLOCK_SIZE];
    AES_encrypt(plaintext, ciphertext, &aesKey);

    // ������ܽ��
    std::cout << "Ciphertext: ";
    printHex(ciphertext, AES_BLOCK_SIZE);

    return 0;
}

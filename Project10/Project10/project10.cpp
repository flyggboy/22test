#include <iostream>
#include <string>
#pragma comment(lib,"libssl.lib")
#pragma comment(lib,"libcrypto.lib")
#include <openssl/ec.h>
#include <openssl/ecdsa.h>
#include <openssl/obj_mac.h>

using namespace std;

void generateECKeyPair(EC_KEY*& ecKey)
{
    EC_GROUP* ecGroup = EC_GROUP_new_by_curve_name(NID_secp256k1);
    if (ecGroup == nullptr) {
        cout << "Failed to create EC group." << endl;
        return;
    }

    ecKey = EC_KEY_new();
    if (ecKey == nullptr) {
        cout << "Failed to create EC key." << endl;
        EC_GROUP_free(ecGroup);
        return;
    }

    if (EC_KEY_set_group(ecKey, ecGroup) != 1) {
        cout << "Failed to set EC group for key." << endl;
        EC_KEY_free(ecKey);
        EC_GROUP_free(ecGroup);
        return;
    }

    if (EC_KEY_generate_key(ecKey) != 1) {
        cout << "Failed to generate EC key pair." << endl;
        EC_KEY_free(ecKey);
        EC_GROUP_free(ecGroup);
        return;
    }
}

string signData(const string& data, EC_KEY* privateKey)
{
    const unsigned char* msg = reinterpret_cast<const unsigned char*>(data.c_str());
    size_t msgLen = data.size();

    ECDSA_SIG* signature = ECDSA_do_sign(msg, static_cast<int>(msgLen), privateKey);
    if (signature == nullptr) {
        cout << "Failed to generate ECDSA signature." << endl;
        return "";
    }

    const BIGNUM* r = nullptr;
    const BIGNUM* s = nullptr;
    ECDSA_SIG_get0(signature, &r, &s);

    char* rHex = BN_bn2hex(r);
    char* sHex = BN_bn2hex(s);
    string signatureHex = string(rHex) + string(sHex);

    OPENSSL_free(rHex);
    OPENSSL_free(sHex);
    ECDSA_SIG_free(signature);

    return signatureHex;
}

bool verifySignature(const string& data, const string& signatureHex, EC_KEY* publicKey)
{
    const unsigned char* msg = reinterpret_cast<const unsigned char*>(data.c_str());
    size_t msgLen = data.size();

    BIGNUM* r = BN_new();
    BIGNUM* s = BN_new();
    if (BN_hex2bn(&r, signatureHex.substr(0, 64).c_str()) == 0 ||
        BN_hex2bn(&s, signatureHex.substr(64).c_str()) == 0) {
        BN_free(r);
        BN_free(s);
        return false;
    }

    ECDSA_SIG* signature = ECDSA_SIG_new();
    if (signature == nullptr) {
        BN_free(r);
        BN_free(s);
        return false;
    }

    ECDSA_SIG_set0(signature, r, s);

    int result = ECDSA_do_verify(msg, static_cast<int>(msgLen), signature, publicKey);
    ECDSA_SIG_free(signature);

    return result == 1;
}

int main()
{
    EC_KEY* privateKey = nullptr;
    EC_KEY* publicKey = nullptr;

    generateECKeyPair(privateKey);
    publicKey = EC_KEY_dup(privateKey);

    string data = "Hello, Ethereum!";
    string signature = signData(data, privateKey);

    bool isVerified = verifySignature(data, signature, publicKey);

    if (isVerified) {
        cout << "Signature is verified. Data is authentic." << endl;
    }
    else {
        cout << "Signature verification failed. Data may be tampered with or the wrong public key." << endl;
    }

    EC_KEY_free(privateKey);
    EC_KEY_free(publicKey);

    return 0;
}

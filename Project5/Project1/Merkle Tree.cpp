#include <iostream>
#pragma comment(lib,"libssl.lib")
#pragma comment(lib,"libcrypto.lib")
#include <vector>
#include <string>
#include <iomanip>
#include <openssl/sha.h>
#include <sstream>

class MerkleTree {
public:
    MerkleTree(const std::vector<std::string>& data) {
        leafNodes = data;

        // Build the Merkle tree
        buildTree();
    }

    std::string getRootHash() const {
        return rootHash;
    }

private:
    std::vector<std::string> leafNodes; // Leaf nodes
    std::vector<std::string> internalNodes; // Internal nodes
    std::string rootHash; // Root hash

    void buildTree() {
        if (leafNodes.empty()) {
            std::cout << "No data available.\n";
            return;
        }

        // If the number of leaf nodes is odd, duplicate the last node
        if (leafNodes.size() % 2 != 0) {
            leafNodes.push_back(leafNodes.back());
        }

        while (leafNodes.size() > 1) {
            std::vector<std::string> temp;

            for (size_t i = 0; i < leafNodes.size(); i += 2) {
                std::string concatenatedHash = concatenateAndHash(leafNodes[i], leafNodes[i + 1]);
                internalNodes.push_back(concatenatedHash);
                temp.push_back(concatenatedHash);
            }

            // Update leaf nodes
            leafNodes = temp;
        }

        rootHash = leafNodes[0];
    }

    std::string concatenateAndHash(const std::string& left, const std::string& right) {
        std::string concatenated = left + right;

        unsigned char hash[SHA256_DIGEST_LENGTH];
        SHA256(reinterpret_cast<const unsigned char*>(concatenated.c_str()), concatenated.length(), hash);

        std::stringstream ss;
        for (int i = 0; i < SHA256_DIGEST_LENGTH; i++) {
            ss << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(hash[i]);
        }

        return ss.str();
    }
};

int main() {
    // Create leaf nodes data for building the Merkle tree
    std::vector<std::string> data = {
        "Hello",
        "World",
        "Merkle",
        "Tree"
    };

    // Create Merkle Tree object
    MerkleTree merkleTree(data);

    // Get the root hash value
    std::cout << "Root Hash: " << merkleTree.getRootHash() << std::endl;

    return 0;
}

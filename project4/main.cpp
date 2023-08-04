#include"SM_three_optimize.h"

//通过循环展开对代码进行优化的实现主函数
int main() {
	string str;
	str = "202100460151陶瑞琦";
	cout << "string input :" + str << endl << endl;
	string paddingValue = padding(str);
	cout << "after padding:" << endl;
	for (int i = 0; i < paddingValue.size() / 64; i++) {
		for (int j = 0; j < 8; j++) {
			cout << paddingValue.substr(i * 64 + j * 8, 8) << "  ";
		}
		cout << endl;
	}
	cout << endl;
	string result = iteration(paddingValue);
	cout << "hash value:" << endl;
	cout << result.substr(0, 8) << "  ";
	cout << result.substr(8, 8) << "  ";
	cout << result.substr(16, 8) << "  ";
	cout << result.substr(24, 8) << "  ";
	cout << result.substr(32, 8) << "  ";
	cout << result.substr(40, 8) << "  ";
	cout << result.substr(48, 8) << "  ";
	cout << result.substr(56, 8) << "  ";
	cout << endl << endl;
}

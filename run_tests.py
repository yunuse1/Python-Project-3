import pytest
import sys
import os

# Python'a 'src' klasöründeki app.py'yi nerede bulacağını söylüyoruz
sys.path.append(os.path.join(os.getcwd(), 'src'))

if __name__ == "__main__":
    print("🚀 Temiz kurulum testleri başlatılıyor...")
    # 'tests' klasöründeki her şeyi tara ve çalıştır
    exit_code = pytest.main(["-v", "tests/"])
    sys.exit(exit_code)
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.get_coins import fetch_and_store_popular_coins

if __name__ == '__main__':
    fetch_and_store_popular_coins()
    print('Popüler coinler güncellendi.')

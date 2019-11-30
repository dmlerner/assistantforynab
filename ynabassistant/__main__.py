import ynabassistant as ya
import ynab_api


def main():
    c = ya.ynab.cache.Cache()
    x = ya.ynab.cache.X()
    return c, x

if __name__ == '__main__':
    c, x = main()

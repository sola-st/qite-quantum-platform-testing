import argparse


def hello(name):
    print(f'Hello, {name}!')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Greet a person.')
    parser.add_argument('--name', required=True, help='The person to greet.')
    args = parser.parse_args()
    hello(args.name)

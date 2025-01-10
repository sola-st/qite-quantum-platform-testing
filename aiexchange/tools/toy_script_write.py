import argparse


def hello(name, output_path):
    greeting = f'Hello, {name}!'
    with open(output_path, 'w') as file:
        file.write(greeting)
    print(greeting)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Greet a person and save the greeting to a file.')
    parser.add_argument('--name', required=True, help='The person to greet.')
    parser.add_argument('--output_path', required=True,
                        help='The path to save the greeting.')
    args = parser.parse_args()
    hello(args.name, args.output_path)

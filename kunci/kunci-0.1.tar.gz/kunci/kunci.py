#!/usr/bin/env python3
import argparse
import secrets


def generate_password(
        total_passwords,
        total_characters,
        uppercase_threshold,
        number_threshold,
        punctuation_threshold):
    total_thresholds = (
        uppercase_threshold + punctuation_threshold + number_threshold)
    passwords = []

    assert total_characters >= total_thresholds

    for i in range(total_passwords):
        password = []
        random = secrets.SystemRandom()

        uppers = False
        numbers = False
        punctuations = False
        thresholds = False

        total_lowercase = 0
        total_uppercase = 0
        total_numbers = 0
        total_punctuations = 0

        while not thresholds or not uppers or not numbers or not punctuations:
            generate = random.random() * 10
            if generate < 4:
                total_accepted_lower = (total_characters - total_thresholds)
                if total_lowercase < total_accepted_lower:
                    total_lowercase += 1
                    password.append(chr(random.randint(97, 122)))
                else:
                    thresholds = True
                    continue
            elif generate < 6:
                if total_numbers < number_threshold:
                    total_numbers += 1
                    password.append(chr(random.randint(48, 57)))
                else:
                    numbers = True
                    continue
            elif generate < 8:
                if total_uppercase < uppercase_threshold:
                    total_uppercase += 1
                    password.append(chr(random.randint(65, 90)))
                else:
                    uppers = True
                    continue
            else:
                if total_punctuations < punctuation_threshold:
                    total_punctuations += 1
                    password.append(random.sample('?@$!+-', 1)[0])
                else:
                    punctuations = True
                    continue

        passwords.append(''.join(password))
    return passwords


def run():
    parser = argparse.ArgumentParser(description='Generate password')
    parser.add_argument(
        '--total-passwords',
        default=5,
        type=int,
        help='How many passwords you want to generate')
    parser.add_argument(
        '--total-characters',
        default=8,
        type=int,
        help='How many characters to your passwords',)
    parser.add_argument(
        '--total-uppercase',
        default=2,
        type=int,
        help='How many uppercase to your passwords',)
    parser.add_argument(
        '--total-numbers',
        default=2,
        type=int,
        help='How many numbers to your passwords',)
    parser.add_argument(
        '--total-punctuations',
        default=2,
        type=int,
        help='How many numbers to your passwords',)

    args = parser.parse_args()
    for password in generate_password(
            args.total_passwords,
            args.total_characters,
            args.total_uppercase,
            args.total_numbers,
            args.total_punctuations):

        print(password)

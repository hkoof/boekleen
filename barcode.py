# Genereren on-officiele isbn's
#

import re
re_isbn = re.compile('^[0-9]{12,13}$')

def calc_check_digit(isbn):
    # Return correct check digit voor isbn, ongeacht of
    # er al een check digit in de isbn zit en of ie correct is.
    # Lengte van isbn moet dan wel altijd 12 of 13 zijn.
    #
    isbn = str(isbn)
    if not re_isbn.match(isbn):
        raise ValueError("invalid isbn code")
    even = 0
    odd = 0
    for i in range(12):
        digit = int(isbn[i])
        if i % 2:
            even += digit
        else:
            odd += digit
    check_mod = (3 * even + odd) % 10
    checkdigit = 10 - check_mod if check_mod else 0
    return checkdigit

def generate_isbn_codes(start='979999999999', num=1): 
    # Generate next num isbn-like codes, *decreasing* from start
    #
    result = list()
    start = start[:12]   # strip check digit if present
    for i in range (0, -num, -1):
        code = int(start) + i
        checkdigit = calc_check_digit(code)
        result.append(str(code) + str(checkdigit))
    return result


if __name__ == "__main__":
    for isbn in generate_isbn_codes(num=4):
        print(isbn)

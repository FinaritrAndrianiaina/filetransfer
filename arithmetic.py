import os
import binascii


def convert_bytes(byte):
    return int(binascii.hexlify(byte), 16)


def random(nbits):
    nbytes, rbits = divmod(nbits, 8)

    # Get the random bytes
    randomdata = os.urandom(nbytes)

    # Add the remaining random bits
    if rbits > 0:
        randomvalue = ord(os.urandom(1))
        randomvalue >>= (8 - rbits)
        randomdata = bytes(randomvalue) + randomdata
    return randomdata


def randomint(max, nbit):
    r = convert_bytes(random(nbit))
    s = 0
    while r > max:
        s += 1
        r = convert_bytes(random(nbit))
    return r | 1


def algorithme_deuclide(a, b):
    x = 1
    xx = 0
    y = 0
    yy = 1
    while b != 0:
        q = a//b
        a, b = b, a % b
        xx, x = x - q*xx, xx
        yy, y = y - q*yy, yy
    return (a, x, y)


def modulo_exp(x, k, n):
    """
        utiliser pow(x,k,n) est plus rapide :/
    """
    puiss = 1
    while (k > 0):
        if k % 2 != 0:
            puiss = (puiss*x) % n
        x = x*x % n
        k = k//2
    return puiss


def test_nombre_premier(n, k):
    """Calculates whether n is composite (which is always correct) or prime
    (which theoretically is incorrect with error probability 4**-k), by
    applying Miller-Rabin primality testing.

    For reference and implementation example, see:
    https://en.wikipedia.org/wiki/Miller%E2%80%93Rabin_primality_test

    :param n: Integer to be tested for primality.
    :type n: int
    :param k: Number of rounds (witnesses) of Miller-Rabin testing.
    :type k: int
    :return: False if the number is composite, True if it's probably prime.
    :rtype: bool
    """
    # prevent potential infinite loop when d = 0
    if n < 2:
        return False
    # Decompose (n - 1) to write it as (2 ** r) * d
    # While d is even, divide it by 2 and increase the exponent.
    d = n - 1
    r = 0
    while not (d & 1):
        r += 1
        d >>= 1
    # Test k witnesses.
    for _ in range(k):
        # Generate random integer a, where 2 <= a <= (n - 2)
        a = convert_bytes(random(8)) + 2
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == 1:
                # n is composite.
                return False
            if x == n - 1:
                # Exit inner loop and continue with next witness.
                break
        else:
            # If loop doesn't break, n is composite.
            return False

    return True


def get_exponent(phi):
    i = phi.bit_length()//2
    e = randomint(2**i, i)
    a, _, _ = algorithme_deuclide(phi, e)
    while a != 1:
        e = randomint(2**i, i)
        a, _, _ = algorithme_deuclide(phi, e)
    return e


def obtenir_un_nombre_premier(ordre=2):
    i = 0
    while True:
        i += 1
        x = randomint(2**ordre, ordre)
        if test_nombre_premier(x, 12):
            break
    return x


def convert_str_int(text):
    int_s = str()
    for i in text:
        int_s = f"{int_s}%.3i" % ord(i)
    return int(int_s+'000')


def convert_int_str(m):
    int_s = str()
    m = str(m)
    a = len(m) % 3
    if a:
        m = '0'*(3-a) + m
    k = len(m)
    if '000' not in m[-3:]:
        raise ValueError("Cle de decryptage fausse!")
    for i in range(0, k-3, 3):
        a = m[i:i+3]
        if a is '000':
            break
        int_s = f"{int_s}{chr(int(a))}"
    return int_s




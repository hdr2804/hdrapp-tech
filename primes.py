import sys

def pi(n):
    if n < 2:
        return 0
    size = (n + 1) // 2
    b = bytearray(b"\x01") * size
    b[0] = 0
    import math
    for i in range(3, int(math.isqrt(n)) + 1, 2):
        if b[i // 2]:
            start = i * i // 2
            step = i
            b[start::step] = b"\x00" * ((size - 1 - start) // step + 1)
    return 1 + sum(b)  # +1 for the prime 2; b holds odd candidates only

if __name__ == "__main__":
    data = sys.stdin.read().strip().split()
    n = int(data[0]) if data else 0
    print(pi(n))

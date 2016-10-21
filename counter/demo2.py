import time

def demo(np):
    n = np.n

    # cycle
    for i in range(4 * n):
        for j in range(n):
            np[j] = (0, 0, 0)
        np[i % n] = (255, 255, 255)
        np.write()
        time.sleep_ms(25)

    # bounce
    for i in range(4 * n):
        for j in range(n):
            np[j] = (0, 0, 128)
        if (i // n) % 2 == 0:
            np[i % n] = (0, 0, 0)
        else:
            np[n - 1 - (i % n)] = (0, 0, 0)
        np.write()
        time.sleep_ms(60)

    # fade in/out
    for i in range(0, 4 * 256, 8):
        for j in range(n):
            if (i // 256) % 2 == 0:
                val = i & 0xff
            else:
                val = 255 - (i & 0xff)
            np[j] = (val, 0, 0)
        np.write()

    # clear
    for i in range(n):
        np[i] = (0, 0, 0)
    np.write()

def lfsr(length, seed, mask):
	current_value = seed
	while True:
		current_value = (current_value << 1) % 2**length
		parity = 0
		remaining = current_value & mask
		for digit in range(length, 0, -1):
			if 2**digit <= remaining:
				remaining -= 2**digit
				parity = (parity + 1) % 2
		current_value += parity
		yield current_value

randoms = lfsr(8, 0b00011010, 0b10111001)

def random(np):
	for cycle in range(10*np.n):
		for pixel in range(0, np.n):
			np[pixel] = (next(randoms), next(randoms), next(randoms))

		np.write()
		time.sleep_ms(10)

def getIdDistance(a, b):
	assert len(a) == len(b)
	return sum([(a[i] ^ b[i]) * (1 << (8 * i)) for i in range(len(a))])
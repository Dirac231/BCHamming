mod = int(1e9+7) # a Random BIG Prime number

def ipow(base:int, power:int):
    ret, piv = 1, base
    while power:
        if (power & 1):
            ret = ret * piv % mod
        piv = piv * piv % mod
        power >>= 1
    return ret

def berlekamp_massey(x:list):
    ls, cur = [], []
    lf, ld = 0, 0
    for i in range(len(x)):
        t = 0
        for j in range(len(cur)):
            t = (t + int(x[i-j-1]) * cur[j]) % mod
        if (t-int(x[i])) % mod == 0:
            continue
        if not cur:
            cur = [0] * (i+1)
            lf = i
            ld = (t-int(x[i])) % mod
            continue
        k = -(int(x[i])-t) * ipow(ld, mod-2) % mod
        c = [0] * (i-lf-1)
        c.append(k)
        for j in ls:
            c.append(-j * k % mod)
        if len(c) < len(cur):
            c += [0] * (len(cur)-len(c))
        for j in range(len(cur)):
            c[j] = (c[j]+cur[j]) % mod
        if (i-lf+len(ls)) >= len(cur):
            ls, lf, ld = cur, i, (t-x[i])%mod
        cur = c
    for i in cur:
        i = (i % mod + mod) % mod
    return cur

def get_nth(rec:list, dp:list, n:int):
    m = len(rec)
    s, t = [0]*m, [0]*m
    s[0] = 1
    if m != 1:
        t[1] = 1
    else:
        t[0] = rec[0]
    def mul(v:list, w:list):
        m = len(v)
        t = [0]*(2*m)
        for j in range(m):
            for k in range(m):
                t[j+k] += v[j] * w[k] % mod
                if t[j+k] >= mod:
                    t[j+k] -= mod
        for j in range(2*m-1, m-1, -1):
            for k in range(1, m+1):
                t[j-k] += t[j] * rec[k-1] % mod
                if t[j-k] >= mod:
                    t[j-k] -= mod
        # Resize idk if this is required
        if len(t) < m:
            t += [0]*(m-len(t))
        else:
            t = t[:m]
        return t
    while n:
        if n & 1:
            s = mul(s, t)
        t = mul(t, t)
        n >>= 1
    ret = 0
    for i in range(m):
        ret += s[i] * dp[i] % mod
    return ret % mod

def guess_nth_term(x:list, n:int):
    if n < len(x):
        return x[n]
    v = berlekamp_massey(x)
    if not v:
        return 0
    return get_nth(v, x, n)

if __name__ == '__main__':
    # Be sure that you give enough information so that berlek can guess.
    print('Fibonacci Numbers')
    x1 = [0,0,1,2,3,5,8,13]
    print(guess_nth_term(x1, 16))
    print(guess_nth_term(x1, 4))
    
    print('X to the power of 2')
    x2 = [x**2 for x in range(8)]
    berlekamp = berlekamp_massey(x2)
    print(get_nth(berlekamp, x2, 9))
    print(get_nth(berlekamp, x2, 10))
    print(get_nth(berlekamp, x2, 16))
    print(get_nth(berlekamp, x2, 20))

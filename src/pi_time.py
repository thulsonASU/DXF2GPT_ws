def calculate_pi(iterations):
    pi = 0
    for i in range(iterations):
        pi += ((4.0 * (-1)**i) / (2*i + 1))
        print(pi)
    return pi

# Test the function
print(calculate_pi(1000000))
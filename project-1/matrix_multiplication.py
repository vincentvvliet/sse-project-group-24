def matrix_multiplication(n):
    A = [[i + j for j in range(n)] for i in range(n)]
    B = [[i - j for j in range(n)] for i in range(n)]
    result = [[0] * n for _ in range(n)]
    
    for i in range(n):
        for j in range(n):
            for k in range(n):
                result[i][j] += A[i][k] * B[k][j]
    
    return result

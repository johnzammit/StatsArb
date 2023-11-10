
















a = [3,3,4,5,6,7]

## for indexs, i, j, k, such that i < j < k and (a[i] + a[j] + a[k]) % 5 == 0, 
# count how many triplets exist, and runtime must be O(n^2)


#O)n^2) solution
def countTriplets(arr, n, k):
    counter = 0
    valToIndex = {}
    indexToVal = {}
    for i in range(n):
        if arr[i] not in valToIndex:
            valToIndex[arr[i]] = []
        valToIndex[arr[i]].append(i)
        indexToVal[i] = arr[i]
    for i in range(n):
        for j in range(i+1, n):
            left = k - (arr[i] + arr[j]) % k
            if left in valToIndex and valToIndex[left] > j:
                counter += 1
    return counter

print(countTriplets(a, len(a), 15))

# def find_indices(lst, d):
#     n = len(lst)
#     indices = []
#     for i in range(n - 1):
#         # Create a hash map to store the remainder of the sum and the indices
#         rem_dict = {}
#         for j in range(i + 1, n):
#             # Calculate the remainder of the sum of current pair
#             rem = (lst[i] + lst[j]) % d
#             # Calculate the complement remainder
#             complement = (d - rem) % d
#             # If the complement is in the hash map, add the indices to the result
#             if complement in rem_dict:
#                 for k in rem_dict[complement]:
#                     indices.append((k[0], k[1], j))
#             # Add the current pair to the hash map
#             if rem not in rem_dict:
#                 rem_dict[rem] = []
#             rem_dict[rem].append((i, j))
#     return indices

# print(find_indices([3,3,4,6,7], 3))
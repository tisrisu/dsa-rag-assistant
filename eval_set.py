EVAL_SET= [
    #paraphrase
    {"question": "find the element that shows up more than half the time", "expected": ["majority_element.cpp"]},
    {"question": "best day to buy and sell a share for maximum profit", "expected": ["stock_buy_sell.cpp"]},
    {"question": "which number appears once when every other appears twice", "expected": ["single_number.cpp"]},
    {"question": "Given an array of integers, find the total number of pairs where a larger number appears before a smaller number.", "expected": ["count_inversions.cpp", "count_inversions_optimal.cpp"]},
    {"question": "Given an array of integers, return a list of all elements that are strictly greater than every element appearing to their right.", "expected": ["leader_in_arr.cpp"]},
    {"question": "Given two sorted integer arrays, merge them into a single sorted array containing all unique elements from both arrays.", "expected": ["union_sorted_arr.cpp"]},

    #confusable
    {"question": "check whether the array is sorted and then rotated", "expected": ["sorted_arr_rotated.cpp"]},
    {"question": "count subarrays whose elements add up to k", "expected": ["subarray_sum_equals_k.cpp"]},
    {"question": "longest stretch of elements adding up to k", "expected": ["longest_subarr_sum_k.cpp"]},
    {"question": "Given an array of size n, find the element that appears strictly more than n/2 times, assuming one always exists", "expected": ["majority_element.cpp"]},
    {"question": "Given an array of integers of size n, find all elements that appear strictly more than n/3 times", "expected": ["majority_elements_2.cpp"]},

    #more than one file
    {"question": "find four numbers that add up to a target", "expected": ["4Sum_brute_force.cpp", "4Sum_optimal.cpp"]},
    {"question": "count subarrays with xor equal to k", "expected": ["sub_array_xor_k.cpp", "sub_array_xor_k_optimal.cpp"]},
    {"question": "count inversions faster than checking every pair", "expected": ["count_inversions_optimal.cpp"]},   

    #name given 
    {"question": "two sum", "expected": ["two_sum_optimal.cpp"]},
    {"question": "next permutation", "expected": ["next_permutation.cpp"]},
    {"question": "merge overlapping intervals", "expected": ["merge_intervals.cpp"]},
]
HELD_OUT = [
    {"question": "walk through a grid layer by layer starting from the outer edge", "expected": ["print_matrix_spiral_order.cpp"]},
    {"question": "longest run of consecutive numbers in an unsorted array", "expected": ["longest_consecutive_seq.cpp"]},
    {"question": "one number appears twice and another is missing from 1 to n", "expected": ["repeating_missing_numbers.cpp"]},
    {"question": "turn a square grid ninety degrees clockwise in place", "expected": ["rotate_image.cpp"]},
    {"question": "three sum", "expected": ["3_sum.cpp"]},
]

OUT_OF_CORPUS = [
    "what is the capital of India ",
    "how do i reverse a linked list",
    "explain dijkstra algorithm",
    "how do i implement a binary tree in c++",
]
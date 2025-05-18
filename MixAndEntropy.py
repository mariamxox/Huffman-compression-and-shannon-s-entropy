import os
import heapq
from collections import defaultdict
import struct
import time
import math

# Node class for Huffman Tree
class Node:
    def __init__(self, byte=None, frequency=0, left=None, right=None):
        self.byte = byte  # Represents a single byte (0-255)
        self.frequency = frequency
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.frequency < other.frequency


# HuffmanTree class
class HuffmanTree:
    def __init__(self, data=None):
        self.codes = {}
        self.root = self.build_tree(data) if data else None
        if self.root:
            self.generate_codes(self.root, "")

    def build_tree(self, data):
        frequency_map = defaultdict(int)
        for byte in data:
            frequency_map[byte] += 1

        heap = [Node(byte=byte, frequency=freq) for byte, freq in frequency_map.items()]
        heapq.heapify(heap)

        while len(heap) > 1:
            left = heapq.heappop(heap)
            right = heapq.heappop(heap)
            merged = Node(frequency=left.frequency + right.frequency, left=left, right=right)
            heapq.heappush(heap, merged)

        return heap[0] if heap else None

    def generate_codes(self, node, current_code):
        if not node:
            return

        if node.byte is not None:
            self.codes[node.byte] = current_code
            return

        self.generate_codes(node.left, current_code + "0")
        self.generate_codes(node.right, current_code + "1")

    def encode(self, data):
        return "".join(self.codes[byte] for byte in data)


# Convert to binary string
def to_binary_string(encoded_data):
    padding = 8 - len(encoded_data) % 8
    padded_data = encoded_data + "0" * padding
    return padded_data, padding


# Compress file
def compress_file(input_file):
    if not os.path.exists(input_file):
        print("Error: File not found. Please check the file path.")
        return None, None, 0

    try:
        with open(input_file, "rb") as file:
            data = file.read()
    except IOError:
        print(f"Error: Unable to read file {input_file}.")
        return None, None, 0

    if not data:
        print(f"Error: {input_file} is empty.")
        return None, None, 0

    huffman_tree = HuffmanTree(data)
    encoded_data = huffman_tree.encode(data)
    binary_data, padding = to_binary_string(encoded_data)

    # Save as binary string of 0s and 1s
    compressed_file = os.path.splitext(input_file)[0] + "_compressed.huff"
    with open(compressed_file, "w") as file:
        file.write(f"{padding}\n")  # Store the padding as the first line
        file.write(binary_data)  # Write the actual binary data

    return huffman_tree, compressed_file, len(data)


# Decompress file
def decompress_file(compressed_file, huffman_tree, original_extension):
    if not os.path.exists(compressed_file):
        print("Error: Compressed file not found.")
        return

    with open(compressed_file, "r") as file:
        padding = int(file.readline().strip())  # Read the padding
        binary_data = file.read()  # Read the binary data

    if not binary_data:
        print(f"Error: No data found in {compressed_file}.")
        return

    binary_string = binary_data
    binary_string = binary_string[:-padding]  # Remove padding

    decoded_data = decode_huffman(binary_string, huffman_tree)

    decompressed_file = compressed_file.replace("_compressed.huff", "_decompressed" + original_extension)
    with open(decompressed_file, "wb") as file:
        file.write(decoded_data)
    print(f"Decompressed file saved as: {decompressed_file}")


# Decode Huffman
def decode_huffman(binary_string, huffman_tree):
    node = huffman_tree.root
    decoded_data = bytearray()

    for bit in binary_string:
        node = node.left if bit == "0" else node.right
        if node.byte is not None:
            decoded_data.append(node.byte)
            node = huffman_tree.root

    return decoded_data


# Calculate Shannon's Entropy
def shannons_entropy(data):
    frequency_map = defaultdict(int)
    for byte in data:
        frequency_map[byte] += 1

    entropy = 0
    total_bytes = len(data)
    for freq in frequency_map.values():
        probability = freq / total_bytes
        entropy -= probability * math.log2(probability)

    return entropy


# Compare files
def compare_files(file1, file2):
    with open(file1, "rb") as f1, open(file2, "rb") as f2:
        return f1.read() == f2.read()


# Main
if __name__ == "__main__":
    print("Choose the file type to compress:")
    print("1. File")
    print("2. Image")
    print("3. Music (MP3)")

    choice = input("Enter your choice: ")

    if choice == "1":
        input_file = r #"file path"
        file_extension = ".txt"
    elif choice == "2":
        input_file = r #"file path"
        file_extension = ".jpg"
    elif choice == "3":
        input_file = r #"file path"
        file_extension = ".mp3"
    else:
        print("Invalid choice.")
        exit()

    # Read the file data and calculate Shannon's entropy
    try:
        with open(input_file, "rb") as file:
            data = file.read()

        entropy = shannons_entropy(data)
        print(f"Shannon's Entropy of the file: {entropy:.4f} bits per byte")
    except FileNotFoundError:
        print(f"Error: File {input_file} not found.")
        exit()

    # Compression
    start_time = time.time()
    huffman_tree, compressed_file, original_size = compress_file(input_file)
    compression_time = time.time() - start_time

    if huffman_tree is None:
        exit()

    compressed_size = os.path.getsize(compressed_file)
    compression_ratio = compressed_size / original_size
    compression_efficiency = (1 - compression_ratio) * 100

    print(f"Original file size: {original_size} bytes")
    print(f"Compressed file size: {compressed_size} bytes")
    print(f"Compression efficiency: {compression_efficiency:.2f}%")
    print(f"Time taken to compress: {compression_time:.4f} seconds")
    print("Huffman compression completed")

    # Decompression
    start_time = time.time()
    decompress_file(compressed_file, huffman_tree, file_extension)
    decompression_time = time.time() - start_time

    print(f"Time taken to decompress: {decompression_time:.4f} seconds")

    # Comparison
    decompressed_file = compressed_file.replace("_compressed.huff", "_decompressed" + file_extension)
    if compare_files(input_file, decompressed_file):
        print("Decompression successful. The files are the same.")
    else:
        print("Decompression failed. The files are different.")

import os
import heapq
from collections import defaultdict
import struct
import time


# Node class
class Node:
    def __init__(self, character=None, frequency=0, left=None, right=None):
        self.character = character
        self.frequency = frequency
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.frequency < other.frequency


# HuffmanTree class
class HuffmanTree:
    def __init__(self, text=None, codes=None):
        self.codes = codes or {}
        self.root = self.build_tree(text) if text else None
        if self.root:
            self.generate_codes(self.root, "")

    # Build tree
    def build_tree(self, text):
        frequency_map = defaultdict(int)
        for ch in text:
            frequency_map[ch] += 1

        heap = [Node(character=char, frequency=freq) for char, freq in frequency_map.items()]
        heapq.heapify(heap)

        while len(heap) > 1:
            left = heapq.heappop(heap)
            right = heapq.heappop(heap)
            merged = Node(frequency=left.frequency + right.frequency, left=left, right=right)
            heapq.heappush(heap, merged)

        return heap[0] if heap else None

    # Generate codes
    def generate_codes(self, node, current_code):
        if not node:
            return

        if node.character is not None:
            self.codes[node.character] = current_code
            return

        self.generate_codes(node.left, current_code + "0")
        self.generate_codes(node.right, current_code + "1")

    # Encode text
    def encode(self, text):
        return "".join(self.codes[ch] for ch in text)


# Convert to binary
def to_binary_string(encoded_text):
    padding = 8 - len(encoded_text) % 8
    padded_text = encoded_text + "0" * padding
    binary_data = bytearray()

    for i in range(0, len(padded_text), 8):
        byte = padded_text[i:i+8]
        binary_data.append(int(byte, 2))

    return binary_data, padding


# Compress file
def compress_file(input_file, compressed_file):
    if not os.path.exists(input_file):
        print("File not found. Make sure the file path is correct.")
        return None, 0

    with open(input_file, "r") as file:
        text = file.read()

    huffman_tree = HuffmanTree(text)
    encoded_text = huffman_tree.encode(text)
    binary_data, padding = to_binary_string(encoded_text)

    with open(compressed_file, "wb") as file:
        file.write(struct.pack("B", padding))
        file.write(binary_data)

    return huffman_tree, len(text), encoded_text


# Decompress file
def decompress_file(compressed_file, output_file, huffman_tree):
    if not os.path.exists(compressed_file):
        print("Compressed file not found.")
        return

    with open(compressed_file, "rb") as file:
        padding = struct.unpack("B", file.read(1))[0]
        binary_data = file.read()

    binary_string = ""
    for byte in binary_data:
        binary_string += f"{byte:08b}"

    binary_string = binary_string[:-padding]

    decoded_text = decode_huffman(binary_string, huffman_tree)

    with open(output_file, "w") as file:
        file.write(decoded_text)

    print(f"Decompressed file saved as: {output_file}")


# Decode binary
def decode_huffman(binary_string, huffman_tree):
    node = huffman_tree.root
    decoded_text = ""

    for bit in binary_string:
        if bit == "0":
            node = node.left
        else:
            node = node.right

        if node.character is not None:
            decoded_text += node.character
            node = huffman_tree.root

    return decoded_text


# Compare files
def compare_files(file1, file2):
    with open(file1, "r") as f1, open(file2, "r") as f2:
        return f1.read() == f2.read()


# Main
if __name__ == "__main__":
    input_file = r #"file path"
    
    # Extract the base name of the input file (without extension)
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    
    # Set the directory (Desktop) where files should be saved
    desktop_dir = r #"Desktop path"
    
    # Dynamically generate the paths for the compressed and decompressed files on the Desktop
    compressed_file = os.path.join(desktop_dir, f"{base_name}_compressed.huff")
    decompressed_file = os.path.join(desktop_dir, f"{base_name}_decompressed.txt")
    compressed_text_file = os.path.join(desktop_dir, f"{base_name}_compressed_output.txt")
    

    # Compression
    start_time = time.time()
    result = compress_file(input_file, compressed_file)
    compression_time = time.time() - start_time

    if result is None:
        exit()

    huffman_tree, original_size, encoded_text = result
    compressed_size = os.path.getsize(compressed_file)
    compression_ratio = compressed_size / original_size
    compression_efficiency = (1 - compression_ratio) * 100

    with open(compressed_text_file, "w") as file:
        file.write(encoded_text)

    print(f"Original file size: {original_size} bytes")
    print(f"Compressed file size: {compressed_size} bytes")
    print(f"Compression efficiency: {compression_efficiency:.2f}%")
    print(f"Time taken to compress: {compression_time:.4f} seconds")
    print(f"Compression saved as: {compressed_text_file}")

    print("Huffman compression completed")

    # Decompression
    start_time = time.time()
    decompress_file(compressed_file, decompressed_file, huffman_tree)
    decompression_time = time.time() - start_time
    print(f"Time taken to decompress: {decompression_time:.4f} seconds")


    # Comparison
    if compare_files(input_file, decompressed_file):
        print("Decompression successful. The files are the same.")
    else:
        print("Decompression failed. The files are different.")

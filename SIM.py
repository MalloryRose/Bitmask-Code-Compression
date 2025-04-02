# On my honor, I have neither given nor received unauthorized aid on this assignment

class CodeCompression:
    def __init__(self):
        self.binary_code = []
        self.original_binary = []
        self.dictionary = [''] * 16

    def get_binary_code(self):
        return self.binary_code

    def read_binary_file(self, filename):
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                if line:
                    self.binary_code.append(line)
                    self.original_binary.append(line)

    def write_compressed_file(self, filename):
        with open(filename, 'w') as file:
            code_string = ''.join(self.binary_code)
            num_zeros = 32 - (len(code_string) % 32) if len(code_string) % 32 != 0 else 0
            
            for i in range(0, len(code_string), 32):
                if i + 32 > len(code_string):
                    file.write(code_string[i:])
                    file.write('0' * num_zeros)
                    file.write('\n')
                else:
                    file.write(code_string[i:i+32] + '\n')
            
            file.write('xxxx\n')
            for entry in self.dictionary:
                file.write(entry + '\n')

    def write_decompressed_file(self, filename):
        with open(filename, 'w') as file:
            for pattern in self.binary_code:
                file.write(pattern + '\n')

    def compress(self):
        self.set_dictionary()
        self.direct_matching()
        self.bitmask()
        self.bit_mismatch1()
        self.bit_mismatch2_consecutive()
        self.bit_mismatch4()
        self.bit_separated2()
        self.uncompressed()
        self.rle()

    def decompress(self, filename):
        # Read the compressed file
        with open(filename, 'r') as file:
            lines = file.readlines()
        
        # Extract compressed data and dictionary
        compressed_lines = []
        dictionary_section = False
        dict_idx = 0
        
        for line in lines:
            line = line.strip()
            if line == 'xxxx':
                dictionary_section = True
                continue
            if dictionary_section:
                if dict_idx < 16:
                    self.dictionary[dict_idx] = line
                    dict_idx += 1
            else:
                compressed_lines.append(line)
        
        # Concatenate all compressed lines into a single bit string
        bit_string = ''.join(compressed_lines)
        
        # Parse the bit string into individual patterns
        self.binary_code = []
        i = 0
        last_pattern = None  # To handle RLE
        
        while i < len(bit_string):
            # Ensure we have at least 3 bits to read the format
            if i + 3 > len(bit_string):
                break
            
            format_type = bit_string[i:i+3]
            i += 3
            
            if format_type == '000':  # Original Binary (35 bits total)
                if i + 32 > len(bit_string):
                    break
                pattern = bit_string[i:i+32]
                self.binary_code.append(pattern)
                i += 32
            
            elif format_type == '001':  # RLE (6 bits total)
                if i + 3 > len(bit_string):
                    break
                count = int(bit_string[i:i+3], 2) + 1  # Number of additional occurrences
                i += 3
                # RLE repeats the last pattern
                if last_pattern:
                    for _ in range(count):
                        self.binary_code.append(last_pattern)
                else:
                    # If no last pattern, skip (shouldn't happen in valid input)
                    continue
            
            elif format_type == '010':  # Bitmask (17 bits total)
                if i + 14 > len(bit_string):
                    break
                start_loc = int(bit_string[i:i+5], 2)
                i += 5
                bitmask = bit_string[i:i+4]
                i += 4
                dict_idx = int(bit_string[i:i+4], 2)
                i += 4
                result = self.decompress_bitmask(start_loc, bitmask, dict_idx)
                self.binary_code.append(result)
                last_pattern = result
            
            elif format_type == '011':  # 1-bit Mismatch (14 bits total)
                if i + 11 > len(bit_string):
                    break
                mismatch_loc = int(bit_string[i:i+5], 2)
                i += 5
                dict_idx = int(bit_string[i:i+4], 2)
                i += 4
                result = self.decompress_1bit_mismatch(mismatch_loc, dict_idx)
                self.binary_code.append(result)
                last_pattern = result
            
            elif format_type == '100':  # 2-bit Consecutive (14 bits total)
                if i + 11 > len(bit_string):
                    break
                start_loc = int(bit_string[i:i+5], 2)
                i += 5
                dict_idx = int(bit_string[i:i+4], 2)
                i += 4
                result = self.decompress_2bit_consecutive(start_loc, dict_idx)
                self.binary_code.append(result)
                last_pattern = result
            
            elif format_type == '101':  # 4-bit Consecutive (14 bits total)
                if i + 11 > len(bit_string):
                    break
                start_loc = int(bit_string[i:i+5], 2)
                i += 5
                dict_idx = int(bit_string[i:i+4], 2)
                i += 4
                result = self.decompress_4bit_consecutive(start_loc, dict_idx)
                self.binary_code.append(result)
                last_pattern = result
            
            elif format_type == '110':  # 2-bit Anywhere (19 bits total)
                if i + 16 > len(bit_string):
                    break
                first_ml = int(bit_string[i:i+5], 2)
                i += 5
                second_ml = int(bit_string[i:i+5], 2)
                i += 5
                dict_idx = int(bit_string[i:i+4], 2)
                i += 4
                result = self.decompress_2bit_anywhere(first_ml, second_ml, dict_idx)
                self.binary_code.append(result)
                last_pattern = result
            
            elif format_type == '111':  # Direct Matching (7 bits total)
                if i + 4 > len(bit_string):
                    break
                dict_idx = int(bit_string[i:i+4], 2)
                i += 4
                result = self.dictionary[dict_idx]
                self.binary_code.append(result)
                last_pattern = result

    def decompress_bitmask(self, start_loc, bitmask, dict_idx):
        result = list(self.dictionary[dict_idx])
        for i in range(4):
            if bitmask[i] == '1':
                result[start_loc + i] = '1' if result[start_loc + i] == '0' else '0'
        return ''.join(result)

    def decompress_1bit_mismatch(self, mismatch_loc, dict_idx):
        result = list(self.dictionary[dict_idx])
        result[mismatch_loc] = '1' if result[mismatch_loc] == '0' else '0'
        return ''.join(result)

    def decompress_2bit_consecutive(self, start_loc, dict_idx):
        result = list(self.dictionary[dict_idx])
        for i in range(2):
            result[start_loc + i] = '1' if result[start_loc + i] == '0' else '0'
        return ''.join(result)

    def decompress_4bit_consecutive(self, start_loc, dict_idx):
        result = list(self.dictionary[dict_idx])
        for i in range(4):
            result[start_loc + i] = '1' if result[start_loc + i] == '0' else '0'
        return ''.join(result)

    def decompress_2bit_anywhere(self, first_ml, second_ml, dict_idx):
        result = list(self.dictionary[dict_idx])
        result[first_ml] = '1' if result[first_ml] == '0' else '0'
        result[second_ml] = '1' if result[second_ml] == '0' else '0'
        return ''.join(result)

    def rle(self):
        i = 0
        while i < len(self.binary_code) - 1:
            if self.binary_code[i] == self.binary_code[i + 1]:
                count = 0
                while (i + count + 1 < len(self.binary_code) and 
                       self.binary_code[i] == self.binary_code[i + count + 1] and 
                       count < 8):
                    count += 1
                if count > 0:
                    self.binary_code[i + 1] = f'001{count-1:03b}'
                    if count > 1:
                        del self.binary_code[i + 2:i + count + 1]
            i += 1

    def uncompressed(self):
        for i in range(len(self.binary_code)):
            if self.binary_code[i] == self.original_binary[i]:
                self.binary_code[i] = '000' + self.binary_code[i]

    def set_dictionary(self):
        freq_map = {}
        first_occurrence = []
        
        for i, pattern in enumerate(self.original_binary):
            freq_map[pattern] = freq_map.get(pattern, 0) + 1
            if pattern not in [x[0] for x in first_occurrence]:
                first_occurrence.append((pattern, i))
        
        freq_list = sorted(freq_map.items(), key=lambda x: (-x[1], 
                          next(entry[1] for entry in first_occurrence if entry[0] == x[0])))
        
        for i, (pattern, _) in enumerate(freq_list[:16]):
            self.dictionary[i] = pattern

    def direct_matching(self):
        for i in range(len(self.binary_code)):
            for j in range(16):
                if self.dictionary[j] and self.binary_code[i] == self.dictionary[j]:
                    self.binary_code[i] = f'111{j:04b}'
                    break

    def bitmask(self):
        for i in range(len(self.binary_code)):
            if self.binary_code[i][:3] in ['111']:
                continue
            current = self.original_binary[i]
            for dict_idx in range(16):
                if not self.dictionary[dict_idx]:
                    continue
                dict_entry = self.dictionary[dict_idx]
                for start_pos in range(28):
                    bitmask = ['0'] * 4
                    valid_mask = False
                    for j in range(4):
                        if start_pos + j < 32 and dict_entry[start_pos + j] != current[start_pos + j]:
                            bitmask[j] = '1'
                            valid_mask = True
                    if valid_mask and bitmask[0] == '1':
                        modified = list(dict_entry)
                        for j in range(4):
                            if bitmask[j] == '1':
                                modified[start_pos + j] = '1' if modified[start_pos + j] == '0' else '0'
                        if ''.join(modified) == current:
                            self.binary_code[i] = f'010{start_pos:05b}{"".join(bitmask)}{dict_idx:04b}'
                            break

    def bit_mismatch1(self):
        for i in range(len(self.binary_code)):
            if self.binary_code[i][:3] in ['111', '010']:
                continue
            current = self.original_binary[i]
            for dict_idx in range(16):
                if not self.dictionary[dict_idx]:
                    continue
                dict_entry = self.dictionary[dict_idx]
                diff_count = 0
                diff_pos = -1
                for j in range(32):
                    if current[j] != dict_entry[j]:
                        diff_count += 1
                        diff_pos = j
                if diff_count == 1:
                    self.binary_code[i] = f'011{diff_pos:05b}{dict_idx:04b}'
                    break

    def bit_mismatch2_consecutive(self):
        for i in range(len(self.binary_code)):
            if self.binary_code[i][:3] in ['111', '010', '011']:
                continue
            current = self.original_binary[i]
            for dict_idx in range(16):
                if not self.dictionary[dict_idx]:
                    continue
                dict_entry = self.dictionary[dict_idx]
                for start_pos in range(31):
                    if (current[start_pos] != dict_entry[start_pos] and 
                        current[start_pos + 1] != dict_entry[start_pos + 1]):
                        all_other_match = all(current[j] == dict_entry[j] 
                                            for j in range(32) 
                                            if j not in [start_pos, start_pos + 1])
                        if all_other_match:
                            self.binary_code[i] = f'100{start_pos:05b}{dict_idx:04b}'
                            break

    def bit_mismatch4(self):
        for i in range(len(self.binary_code)):
            if self.binary_code[i][:3] in ['111', '010', '011', '100']:
                continue
            current = self.original_binary[i]
            for dict_idx in range(16):
                if not self.dictionary[dict_idx]:
                    continue
                dict_entry = self.dictionary[dict_idx]
                for start_pos in range(29):
                    diff_count = sum(1 for j in range(4) if current[start_pos + j] != dict_entry[start_pos + j])
                    if diff_count == 4:
                        all_other_match = all(current[j] == dict_entry[j] 
                                            for j in range(32) 
                                            if j < start_pos or j >= start_pos + 4)
                        if all_other_match:
                            self.binary_code[i] = f'101{start_pos:05b}{dict_idx:04b}'
                            break

    def bit_separated2(self):
        for i in range(len(self.binary_code)):
            if self.binary_code[i][:3] in ['111', '010', '011', '100', '101']:
                continue
            current = self.original_binary[i]
            for dict_idx in range(16):
                if not self.dictionary[dict_idx]:
                    continue
                dict_entry = self.dictionary[dict_idx]
                diff_positions = [j for j in range(32) if current[j] != dict_entry[j]]
                if len(diff_positions) == 2 and diff_positions[1] - diff_positions[0] != 1:
                    self.binary_code[i] = f'110{diff_positions[0]:05b}{diff_positions[1]:05b}{dict_idx:04b}'
                    break

if __name__ == '__main__':
    import sys
    compressor = CodeCompression()
    
    mode = sys.argv[1]
    if mode == '1':
        compressor.read_binary_file('original.txt')
        compressor.compress()
        compressor.write_compressed_file('cout.txt')
    elif mode == '2':
        compressor.decompress('compressed.txt')
        compressor.write_decompressed_file('dout.txt')
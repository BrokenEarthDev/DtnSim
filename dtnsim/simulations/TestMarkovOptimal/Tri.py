import os

def main():
    try:
        # Get the directory where this script is located and build full path for File1.txt
        script_dir = os.path.dirname(os.path.abspath(__file__))
        infile_path = os.path.join(script_dir, "File1.txt")
        
        # Open File1.txt and filter lines that begin with "With" and end with "2" or "4"
        lines_ending_with_2 = []
        lines_ending_with_4 = []
        random_place_count = 0  # Counter for "Random place" occurrences
        
        with open(infile_path, "r") as infile:
            for line in infile:
                # Count occurrences of "Random place" in the line
                random_place_count += line.count("Random place")
                
                if line.startswith("With"):
                    stripped_line = line.rstrip()
                    if stripped_line.endswith("2"):
                        lines_ending_with_2.append(line)
                    elif stripped_line.endswith("4"):
                        lines_ending_with_4.append(line)
        
        # Combine filtered lines - first all lines ending with 2, then all lines ending with 4
        filtered_lines = lines_ending_with_2 + lines_ending_with_4
        
        # Write the filtered lines into output.txt (in the same directory)
        outfile_path = os.path.join(script_dir, "output.txt")
        with open(outfile_path, "w") as outfile:
            outfile.writelines(filtered_lines)

        total_lines = len(lines_ending_with_2) + len(lines_ending_with_4)
        print(f"{total_lines} line(s) written to output.txt.")
        print(f"The phrase 'Random place' appears {random_place_count} time(s) in File1.txt.")
    except FileNotFoundError:
        print("File1.txt not found.")

if __name__ == "__main__":
    main()
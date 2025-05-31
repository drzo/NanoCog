import os
import glob
import requests
import tiktoken
import numpy as np

def download_file(url,_output_path):
    """Downloads a file from a URL and saves it locally."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
        with open(_output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Successfully downloaded {url} to {_output_path}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}")
        return False

def read_file_content(file_path):
    """Reads and returns the content of a local file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Warning: File not found {file_path}, skipping.")
        return ""
    except Exception as e:
        print(f"Error reading file {file_path}: {e}, skipping.")
        return ""

if __name__ == '__main__':
    # Define the output directory for this script's files (train.bin, val.bin)
    # This script is expected to be in nanoGPT/data/cogprime/
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = current_script_dir
    os.makedirs(output_dir, exist_ok=True)

    # --- Define Data Sources ---
    all_text_content = []
    separator = "\n\n<|endofdocument|>\n\n" # Using a separator might help the model

    # 1. CogPrime Main Paper (Fetch from GitHub)
    cogprime_paper_url = "https://raw.githubusercontent.com/drzo/cogprime/main/CogPrime%20-%20An%20Integrative%20Architecture%20for%20Embodied%20Artificial%20General%20Intelligence.md"
    cogprime_paper_local_path = os.path.join(output_dir, "cogprime_paper.md")
    print(f"Processing CogPrime Main Paper from URL: {cogprime_paper_url}")
    if download_file(cogprime_paper_url, cogprime_paper_local_path):
        content = read_file_content(cogprime_paper_local_path)
        if content:
            all_text_content.append(content)
            all_text_content.append(separator)

    # 2. opencog-central Documentation
    # Assuming opencog-central is a sibling directory to nanoGPT parent, or adjust paths as needed.
    # Path relative to this script: ../../opencog-central/
    opencog_central_base_path = os.path.abspath(os.path.join(current_script_dir, "..", "..", "opencog-central"))
    print(f"Attempting to read opencog-central docs from: {opencog_central_base_path}")

    opencog_docs_files = [
        "README.md",
        "docs/CogPrime_Integrative_Architecture_AGI.md",
        "docs/IMPLEMENTATION_GUIDE.md",
        "docs/COGPRIME_STATUS_2024.md",
        "docs/COGPRIME_ARCHITECTURE_DIAGRAM.md",
        "examples/SIMPLE_COGPRIME_AGENT.md",
        "profile/README.md"
    ]

    for doc_file in opencog_docs_files:
        file_path = os.path.join(opencog_central_base_path, doc_file)
        print(f"Processing opencog-central doc: {file_path}")
        content = read_file_content(file_path)
        if content:
            all_text_content.append(content)
            all_text_content.append(separator)

    # 3. opencog-central Scheme Files
    scheme_files_path_pattern = os.path.join(opencog_central_base_path, "Scheme", "**", "*.scm")
    print(f"Processing opencog-central Scheme files from pattern: {scheme_files_path_pattern}")
    scheme_files = glob.glob(scheme_files_path_pattern, recursive=True)

    if not scheme_files:
        print(f"Warning: No Scheme files found at {scheme_files_path_pattern}. Check the path.")
    else:
        print(f"Found {len(scheme_files)} Scheme files.")

    for scm_file in scheme_files:
        print(f"Processing Scheme file: {scm_file}")
        content = read_file_content(scm_file)
        if content:
            all_text_content.append(f"\n\n--- Scheme File: {os.path.basename(scm_file)} ---\n")
            all_text_content.append(content)
            all_text_content.append(separator)
    
    if not all_text_content:
        print("No content collected. Exiting. Please check data source paths and availability.")
        exit(1)

    # Concatenate all collected text
    full_text_data = "".join(all_text_content)
    print(f"Total length of combined text data: {len(full_text_data)} characters")

    # --- Tokenization ---
    print("Tokenizing data with GPT-2 tokenizer...")
    enc = tiktoken.get_encoding("gpt2")
    token_ids = enc.encode_ordinary(full_text_data) # encode_ordinary for gpt2 is fine
    print(f"Total number of tokens: {len(token_ids)}")
    print(f"Vocabulary size: {enc.n_vocab}")

    # --- Data Splitting ---
    n_tokens = len(token_ids)
    train_ratio = 0.9
    split_idx = int(n_tokens * train_ratio)

    train_data_ids = token_ids[:split_idx]
    val_data_ids = token_ids[split_idx:]

    print(f"Training set: {len(train_data_ids)} tokens")
    print(f"Validation set: {len(val_data_ids)} tokens")

    # --- Saving to .bin files ---
    train_ids_np = np.array(train_data_ids, dtype=np.uint16)
    val_ids_np = np.array(val_data_ids, dtype=np.uint16)

    train_output_path = os.path.join(output_dir, 'train.bin')
    val_output_path = os.path.join(output_dir, 'val.bin')

    print(f"Saving training data to {train_output_path}...")
    train_ids_np.tofile(train_output_path)

    print(f"Saving validation data to {val_output_path}...")
    val_ids_np.tofile(val_output_path)

    print("Data preparation complete.")
    print(f"Output files train.bin and val.bin are in: {output_dir}")
    print("You can now train nanoGPT using these files, for example:")
    print(f"python train.py data/cogprime/config_cogprime.py (You'll need to create this config file)")

    # Clean up downloaded paper if it exists
    if os.path.exists(cogprime_paper_local_path):
        try:
            os.remove(cogprime_paper_local_path)
            print(f"Cleaned up temporary file: {cogprime_paper_local_path}")
        except OSError as e:
            print(f"Error deleting temporary file {cogprime_paper_local_path}: {e}")


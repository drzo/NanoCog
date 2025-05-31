"""
Sample from a CogPrime-trained nanoGPT model.
This script is adapted from the original sample.py in nanoGPT,
with defaults and example prompts tailored for models trained on
the CogPrime architecture corpus (AGI theory, OpenCog docs, Scheme code).
"""
import os
import pickle
from contextlib import nullcontext
import torch
import tiktoken
from model import GPTConfig, GPT

# -----------------------------------------------------------------------------
# Configuration (Defaults for CogPrime models)
# -----------------------------------------------------------------------------
init_from = 'resume' # 'resume' (from out_dir) or 'gpt2*' or 'scratch'
out_dir = 'out-cogprime' # ignored if init_from is not 'resume'
start = "\n" # or "<|endoftext|>" or etc. Can also specify a file, see help
num_samples = 3 # number of samples to draw
max_new_tokens = 250 # number of tokens generated in each sample
temperature = 0.8 # 1.0 = no change, < 1.0 = less random, > 1.0 = more random, in predictions
top_k = 200 # retain only the top_k most likely tokens, clamp others to have 0 probability
seed = 1337
device = 'cuda' # examples: 'cpu', 'cuda', 'cuda:0', 'cuda:1', etc.
dtype = 'bfloat16' if torch.cuda.is_available() and torch.cuda.is_bf16_supported() else 'float16' # 'float32' or 'bfloat16' or 'float16'
compile = False # use PyTorch 2.0 to compile the model to be faster

# Example prompts specific to CogPrime and AGI:
# You can uncomment one of these or provide your own via --start="YOUR PROMPT"
example_prompts = [
    "Explain the concept of Cognitive Synergy in the CogPrime architecture:",
    "The AtomSpace in OpenCog is primarily used for:",
    "A key difference between PLN and traditional logic is:",
    "MOSES is an algorithm for procedural learning. It works by:",
    "To implement a simple goal in CogPrime, one might represent it as an Atom of type:",
    "How does ECAN contribute to resource allocation in CogPrime?",
    "An example of a Cognitive Schematic (Context -> Procedure -> Goal) would be:",
    "(define-atomspace my-as", # For Scheme code generation
    "```scheme\n; A simple OpenCog Scheme function to count incoming links\n(define (count-incoming-links node-handle)\n", # For more structured Scheme
    "The Glocal Memory principle in CogPrime suggests that knowledge is stored:",
    "To train nanoGPT on a new corpus like CogPrime documents, the first step is to:",
    "Figure 7 in the CogPrime paper illustrates the relationship between:",
    "One of the key claims of the CogPrime architecture is that general intelligence can be achieved via:",
    "If an AGI system is placed in an environment which is hierarchically structured, then PLN and pattern mining:",
    "The 'Cognitive Equation' in CogPrime refers to the dynamic of:"
]
# To use an example prompt, you could modify the 'start' variable above or pass it via command line.
# For instance, to use the first example prompt:
# start = example_prompts[0]
# Or from command line:
# python sample_cogprime.py --start="Explain the concept of Cognitive Synergy in the CogPrime architecture:"

exec(open('configurator.py').read()) # overrides from command line or config file
# -----------------------------------------------------------------------------

torch.manual_seed(seed)
torch.cuda.manual_seed(seed)
torch.backends.cuda.matmul.allow_tf32 = True # allow tf32 on matmul
torch.backends.cudnn.allow_tf32 = True # allow tf32 on cudnn
device_type = 'cuda' if 'cuda' in device else 'cpu' # for later use in torch.autocast
ptdtype = {'float32': torch.float32, 'bfloat16': torch.bfloat16, 'float16': torch.float16}[dtype]
ctx = nullcontext() if device_type == 'cpu' else torch.amp.autocast(device_type=device_type, dtype=ptdtype)

# model
if init_from == 'resume':
    # init from a model saved in a specific directory
    ckpt_path = os.path.join(out_dir, 'ckpt.pt')
    checkpoint = torch.load(ckpt_path, map_location=device)
    gptconf = GPTConfig(**checkpoint['model_args'])
    model = GPT(gptconf)
    state_dict = checkpoint['model']
    unwanted_prefix = '_orig_mod.'
    for k,v in list(state_dict.items()):
        if k.startswith(unwanted_prefix):
            state_dict[k[len(unwanted_prefix):]] = state_dict.pop(k)
    model.load_state_dict(state_dict)
elif init_from.startswith('gpt2'):
    # init from a given GPT-2 model
    model = GPT.from_pretrained(init_from, dict(dropout=0.0))

model.eval()
model.to(device)
if compile:
    model = torch.compile(model) # requires PyTorch 2.0 (optional)

# look for the meta pickle in case it is available in the dataset folder
load_meta = False
if init_from == 'resume' and 'config' in checkpoint and 'dataset' in checkpoint['config']: # older checkpoints might not have these...
    meta_path = os.path.join('data', checkpoint['config']['dataset'], 'meta.pkl')
    load_meta = os.path.exists(meta_path)
if load_meta:
    print(f"Loading meta from {meta_path}...")
    with open(meta_path, 'rb') as f:
        meta = pickle.load(f)
    # TODO want to make this more general to arbitrary encoder/decoder schemes
    stoi, itos = meta['stoi'], meta['itos']
    encode = lambda s: [stoi[c] for c in s]
    decode = lambda l: ''.join([itos[i] for i in l])
else:
    # ok let's assume gpt-2 encodings by default
    print("No meta.pkl found, assuming GPT-2 encodings...")
    enc = tiktoken.get_encoding("gpt2")
    encode = lambda s: enc.encode(s, allowed_special={"<|endoftext|>"})
    decode = lambda l: enc.decode(l)

# encode the beginning of the prompt
if start.startswith('FILE:'):
    with open(start[5:], 'r', encoding='utf-8') as f:
        start = f.read()
start_ids = encode(start)
x = (torch.tensor(start_ids, dtype=torch.long, device=device)[None, ...])

# run generation
print(f"\n--- Starting generation from CogPrime-trained model ({out_dir}) ---")
print(f"Prompt: \"{start}\"")
print("---")
with torch.no_grad():
    with ctx:
        for k in range(num_samples):
            y = model.generate(x, max_new_tokens, temperature=temperature, top_k=top_k)
            print(decode(y[0].tolist()))
            print('---------------')

print("\n--- Tips for Prompting CogPrime Models ---")
print("- Be specific: Instead of 'Tell me about AGI', try 'Explain the role of the AtomSpace in CogPrime.'")
print("- Use keywords: Include terms like 'PLN', 'MOSES', 'ECAN', 'cognitive synergy', 'Atomese', 'Scheme'.")
print("- Provide context: For code generation, start with a comment or a partial function definition.")
print("  e.g., --start=\"(define (get-link-strength atom)\"")
print("- Ask for explanations: 'What is the purpose of Glocal Memory according to Goertzel?'")
print("- Explore relationships: 'How does PLN interact with MOSES in the CogPrime architecture?'")
print("- Experiment with temperature: Lower for factual recall (e.g., 0.2-0.5), higher for creative/exploratory text (e.g., 0.8-1.0).")
print("- Use the example prompts list in this script for inspiration!")
print("---")

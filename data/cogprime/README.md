# nanoGPT Training on CogPrime Architecture Corpus

This directory contains scripts and configuration to train a nanoGPT model on a corpus of documents and code related to the **CogPrime** Artificial General Intelligence (AGI) architecture and the **OpenCog** project.

## 1. What is CogPrime and Why Train a Model on It?

**CogPrime** is a comprehensive AGI architecture designed by Dr. Ben Goertzel. It outlines a theoretical and practical blueprint for achieving human-level (and potentially beyond) general intelligence, primarily intended for implementation within the OpenCog framework. The core idea is `OpenCogPrime = OpenCog + CogPrime`.

Training a language model on CogPrime-related materials is interesting because it can lead to a model that:
*   **Understands AGI Concepts:** Learns the vocabulary, core principles, and intricate details of a sophisticated AGI design.
*   **Connects Theory and Practice:** Ingests both high-level architectural papers and lower-level implementation details (like OpenCog Scheme code), potentially learning to bridge the gap.
*   **Generates Relevant Text:** Can produce text discussing AGI, CogPrime components (like PLN, MOSES, ECAN, AtomSpace), cognitive synergy, and even pseudo-code or explanations related to OpenCog's logic.
*   **Aids Research and Development:** Could serve as a knowledgeable assistant for AGI researchers, help in drafting documentation, or explore conceptual variations.

## 2. Data Sources Included

The `prepare.py` script in this directory compiles a corpus from the following sources:

1.  **The CogPrime Main Paper:**
    *   "CogPrime: An Integrative Architecture for Embodied Artificial General Intelligence" by Ben Goertzel. This foundational document details the architecture.
    *   Fetched directly from the `drzo/cogprime` GitHub repository.

2.  **`opencog-central` Repository Documentation:**
    *   The comprehensive documentation recently added to the `drzo/opencog-central` repository, which bridges the 2012 CogPrime vision with the 2024 OpenCog ecosystem status.
    *   This includes:
        *   `README.md` (main overview)
        *   `docs/CogPrime_Integrative_Architecture_AGI.md` (executive summary)
        *   `docs/IMPLEMENTATION_GUIDE.md`
        *   `docs/COGPRIME_STATUS_2024.md`
        *   `docs/COGPRIME_ARCHITECTURE_DIAGRAM.md`
        *   `examples/SIMPLE_COGPRIME_AGENT.md`
        *   `profile/README.md` (OpenCog project overview)
    *   Assumes `opencog-central` is a sibling directory to the parent of `nanoGPT` (e.g., `../opencog-central` relative to `nanoGPT`). You may need to adjust paths in `prepare.py` if your directory structure is different.

3.  **OpenCog Scheme Files:**
    *   Scheme (`.scm`) files from the `Scheme/` directory within the `drzo/opencog-central` repository.
    *   These files reveal the underlying logic and implementation details of various OpenCog components, particularly related to the AtomSpace.

The `prepare.py` script concatenates all this text, using a separator `<|endofdocument|>` between distinct documents/files, to create a single training stream.

## 3. How to Prepare the Data

To prepare the data for training, navigate to the root directory of the `nanoGPT` repository and run:

```bash
python data/cogprime/prepare.py
```

This script will:
1.  Download the CogPrime paper.
2.  Attempt to read the specified documentation and Scheme files from your local `opencog-central` repository clone. **Ensure `opencog-central` is cloned in the correct relative location or update paths in `prepare.py`.**
3.  Tokenize the combined text using the GPT-2 tokenizer (`tiktoken`).
4.  Split the data into training and validation sets (90/10 split by default).
5.  Save the tokenized data as `train.bin` and `val.bin` inside the `data/cogprime/` directory.

If the `opencog-central` repository is not found at the expected relative path (`../../opencog-central` from within `data/cogprime/`), the script will print warnings and proceed with whatever data it *can* find (e.g., just the downloaded CogPrime paper). Check the script's output for any errors or warnings regarding data loading.

## 4. How to Train the Model

Once the `train.bin` and `val.bin` files are successfully created in the `data/cogprime/` directory, you can start training the nanoGPT model.

A sample training configuration is provided in `config/train_cogprime.py`. This configuration sets up a moderately sized GPT model suitable for this custom corpus.

To start training (from the `nanoGPT` root directory):

```bash
python train.py config/train_cogprime.py
```

This command will:
*   Load the hyperparameters from `config/train_cogprime.py`.
*   Use the `dataset = 'cogprime'` setting to find `data/cogprime/train.bin` and `data/cogprime/val.bin`.
*   Train the model, periodically saving checkpoints to the `out-cogprime` directory (or as specified in the config).
*   Log training progress to the console and optionally to Weights & Biases (if configured and `wandb_log = True`).

Training time will depend significantly on your hardware (GPU is highly recommended) and the `max_iters` setting in the configuration file.

## 5. Sample Generation Instructions

After training, or even during training using saved checkpoints, you can generate text samples from your CogPrime-trained model.

From the `nanoGPT` root directory, run:

```bash
python sample.py --out_dir=out-cogprime
```

You can customize sample generation with various flags:
*   `--start="TEXT"`: Provide a starting prompt. For example: `--start="Cognitive synergy in CogPrime is"` or `--start="(define-concept-node"`
*   `--num_samples=N`: Number of samples to generate.
*   `--max_new_tokens=N`: Maximum length of each generated sample.
*   `--temperature=T`: Controls randomness (e.g., 0.8 for more focused, 1.0 for more diverse, 1.2 for more creative/random).
*   `--top_k=K`: Samples from the K most likely next tokens.

Example with a prompt:
```bash
python sample.py --out_dir=out-cogprime --start="The AtomSpace is" --max_new_tokens=150
```

## 6. Expected Results and Applications

A model trained on this corpus is expected to generate text that reflects the style and content of the training data. This could include:
*   **Discussions of AGI theory:** Explanations of CogPrime concepts, arguments for certain architectural choices.
*   **Architectural descriptions:** Text resembling parts of the CogPrime paper or the `opencog-central` documentation.
*   **Pseudo-Scheme code:** Given the Scheme files, the model might attempt to generate code snippets or Atomese-like expressions.
*   **Conceptual connections:** Potentially novel (or at least coherent) connections between different aspects of the CogPrime architecture or OpenCog components.
*   **Question Answering (with prompting):** If prompted with a question about CogPrime, it might generate a plausible answer based on its training.

**Potential Applications:**
*   **AGI Research Assistant:** Brainstorming ideas, drafting sections of papers, summarizing concepts.
*   **Educational Tool:** Helping to explain complex AGI concepts in different ways.
*   **Code/Logic Generation:** Assisting in writing OpenCog Scheme code or Atomese.
*   **Conceptual Exploration:** Generating variations or extensions of CogPrime ideas.

The quality and coherence of the generated text will depend on the model size, training duration, data quality, and hyperparameter tuning.

## 7. Tips for Customization

*   **Data Sources (`prepare.py`):**
    *   **Add more data:** Modify `prepare.py` to include other relevant texts, such as more OpenCog documentation, research papers on related AGI architectures, or even philosophical texts that influenced CogPrime.
    *   **Filter Scheme code:** You might want to preprocess Scheme files, e.g., by removing extensive comments if you want the model to focus more on the code structure.
    *   **Adjust paths:** Ensure the paths to `opencog-central` or other local data sources are correct for your setup.

*   **Training Configuration (`config/train_cogprime.py`):**
    *   **Model Size:** Adjust `n_layer`, `n_head`, `n_embd` to train smaller or larger models depending on your computational resources and goals. Larger models can capture more complex patterns but require more data and VRAM.
    *   **Context Length (`block_size`):** Technical documents and code benefit from longer context. The default is 768, but you can try up to 1024 (GPT-2's limit) if your GPU memory allows.
    *   **Batch Size & Gradient Accumulation:** Modify `batch_size` and `gradient_accumulation_steps` to fit your GPU memory while maintaining a reasonable effective batch size.
    *   **Learning Rate & Iterations:** `learning_rate`, `max_iters`, `warmup_iters`, and `lr_decay_iters` are crucial. You may need to experiment with these, especially if you significantly change the dataset size or model architecture.
    *   **Regularization (`dropout`, `weight_decay`):** Adjust to prevent overfitting, especially if your dataset is relatively small for the model size.

*   **Experimentation:**
    *   Try finetuning a general pre-trained GPT-2 model (e.g., `gpt2` or `gpt2-medium` from OpenAI) on the CogPrime corpus instead of training from scratch. This might yield good results faster. (See nanoGPT's main README for finetuning instructions).
    *   Systematically evaluate the impact of including/excluding Scheme code on the model's understanding and generation capabilities.

Happy training your CogPrime-aware nanoGPT!

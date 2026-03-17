#  Contributing to VidSnapAI

We actively welcome external pull requests!

## Getting Started

1. **Fork the repository** on GitHub.
2. **Clone your fork** down to your local machine.
3. Configure your local environment relying perfectly strictly upon instructions provided in [INSTALLATION.md](INSTALLATION.md).

##  Branch Naming Standards

Please abide strictly by structural prefixes describing your commit intent explicitly securely isolating scopes:

* eature/your-detailed-feature-name (For newly scoped features)
* ugfix/issue-description (For logic fixes)
* docs/updated-files (For README/guide improvements)
* efactor/cleaner-logic (For file structure upgrades)

##  Coding Standards

* **Keep the Pipeline Modular**: Modifications to generating visuals *must* reside within the pipeline/ directory structures. Never pack logic back strictly linearly into generate_process.py or .flask instances.
* **FFmpeg Awareness**: If adding graphical overlays inside 	ransitions.py, test the output natively testing specifically that variable maps (like [v_vfx0]) have sequentially flowed accurately before merging headers.
* **Docstrings Required**: All added Python definitions should contain """ Explanatory string blocks """ explaining their input map types formatting explicit intent cleanly identifying outputs.

##  Pull Request Process

1. Provide concise, active titles mapping intent. 
2. Supply a summary logic defining the core problem + feature.
3. Check the PR matches formatting standard practices.
4. Pass standard local testing rendering 1 clear .mp4 demonstrating correct structural encoding.

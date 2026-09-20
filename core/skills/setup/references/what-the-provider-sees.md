# Material: what the AI provider sees

- Encryption protects the ICM at rest on the host. It does nothing for what is read in a session:
  every file the agent opens is sent to the model, in plain text, over an encrypted connection.
- So the provider can see what the agent read. What it keeps, for how long, and whether it trains
  on it is set by the provider's terms and the owner's privacy settings, not by this kit. The exact
  numbers and the link to the setting are in the adapter's `SKILL.md`, because they differ per provider.
- A cloud session clones the repo into the provider's machine and unlocks it there with the cloud key.
- The trade, said honestly: an ICM that knows you well personalizes better, at the price of putting
  private material in one place and showing it to one provider. A model running on the owner's own
  hardware removes the provider from the picture; the kit does not depend on which model reads the files.
- Practical habits: turn model training off before anything personal goes in; keep other people's
  details to first names and roles; secrets (passwords, tokens, document numbers) never enter the
  ICM at all; "forget" means it leaves every file in the same session.

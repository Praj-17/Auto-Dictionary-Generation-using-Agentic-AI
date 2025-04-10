from litellm import completion
import litellm

# Debugging enablement
litellm._turn_on_debug()
litellm.set_verbose = True

response = completion(
    model="ollama/WizardLM2:7B",
    messages=[{"role": "user", "content": "Test connection"}],
    api_base="http://ollama:11434"  # Use service name, not localhost[2][6]
)

print(response.status_code)  # Should be 200 if the connection is successful
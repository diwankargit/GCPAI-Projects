from sentence_transformers import CrossEncoder


save_path = "./models/cross-encoder-msmarco-MiniLM-L6-v2"

# Download and save
model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2")
model.save(save_path)

print(f"Model saved at {save_path}")

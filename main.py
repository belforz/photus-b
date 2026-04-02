import sys
import os
# import spacy

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
# from infrastructure.adapters.mistral_connector import MistralConnector
# from infrastructure.adapters.spacy_adapter import SpacyAdapter
from infrastructure.adapters.sentence_transformer_adapter import SentenceTransformerAdapter


def main():
    connector = SentenceTransformerAdapter()
    
    sentences = [
    "mostre a melhor foto melancolica"
]
    embeddings = connector.generate_embeddings(texts=sentences)
    for sentence in zip(sentences, embeddings):
        print("Texto", sentence)
        print("Embeddings", embeddings)
    
    
    # processor = SpacyAdapter()
    # text = " O Banco do Brasil anunciou lucros recordes em Brasília. "
    # entities = processor.extract_entities(text)
    # print("Entities:", entities)
    # batch_texts = [
    #     "A Petrobras assinou um contrato no Rio de Janeiro.",
    #     "Marcos viajou para Portugal.",
    #     "A Apple lançou um novo celular hoje."
    # ] * 1000
    # embeddingss = processor.extract_batchs_entities(batch_texts, batch_size=50)
    # print("embeddings of first index:", embeddingss[4])


if __name__ == "__main__":
    main()

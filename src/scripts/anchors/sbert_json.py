import sys
import os
import json
from sentence_transformers import SentenceTransformer

src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from shared.utils.logger import logger


def export_knowledge_anchors_to_json(anchors_dict:dict, output_filepath: str, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
    model = SentenceTransformer(model_name)
    anchors_id = []
    phrases = []

    for name_id, value in anchors_dict.items():
        text_to_split = value[0] if isinstance(value, tuple) else value
        split_phrases =  [phrase.strip() for phrase in text_to_split.split(".") if phrase.strip()]
        for phrase in split_phrases:
            if phrase:
                anchors_id.append(name_id)
                phrases.append(phrase)
        
    emb_arrays = model.encode(phrases, convert_to_numpy=True)
    logger.debug("Embeddings generated")
    emb_list = emb_arrays.tolist()
    logger.debug("Embeddings converted to list")
    payload = {
        "metadata":{
            "model_name": model_name,
            "vector_dimension": emb_arrays.shape[1],
            "total_anchors": len(phrases)
        },
        "anchors_ids": anchors_id,
        "phrases": phrases,
        "embeddings": emb_list
    }
    logger.debug("Payload generated")

    output_dir = os.path.dirname(output_filepath)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(output_filepath, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        logger.info("Knowledge anchors exported to JSON file in {}".format(output_filepath))

if __name__ == "__main__":
    anchors = {
    "Solenidade (Estase)": "Simetria rígida, fundo limpo e minimalista, iluminação suave e equilibrada, cores neutras, estático e pacífico.",

     
    "Conexão (Close-up)": "Sorriso aberto, retrato bem próximo, foco extremo nos olhos, pele nítida, amigável, calor humano, proximidade.",

     
    "Conflito (Caos)": "Sujeira urbana, texturas ásperas e arranhadas, multidão desordenada, cena de rua confusa, poluição visual extrema.",

     
    "Simplicidade (Cotidiano)": "Iluminação natural de janela, saturação média, baixo contraste, ambiente doméstico ordinário, textura comum.",

     
    "Corporativo (Focado)": "Retrato profissional, pessoa focada, fundo liso ou levemente desfocado, iluminação de estúdio neutra e limpa.",


    
    "Vitalidade (Ação)": (
        "Movimento atlético congelado, salto ou corrida, suor visível, luz solar direta e dura, "
        "cores primárias saturadas, composição dinâmica e assimétrica, esporte ao ar livre, "
        "instante de esforço físico, velocidade capturada, adrenalina visual."
    ),

  
    "Distanciamento (Low-key)": (
        "Corredor vazio e sem fim, concreto cinza desgastado, ausência total de pessoas, "
        "abandono urbano, sombra dura e artificial, figura encolhida de costas ignorada pelo ambiente, "
        "silêncio visual, frieza emocional, isolamento em cenário construído e desolado."
    ),

    
    "Sublime (Paisagem)": (
        "Natureza selvagem e intocada, montanha ou oceano imensurável, pôr do sol dramático, "
        "sujeito humano minúsculo diante da grandiosidade natural, maravilhamento e reverência, "
        "céu com nuvens épicas, horizonte infinito, exposição perfeita de paisagem, tirar o fôlego."
    ),

    
    "Nostalgia (Analógico)": (
        "Fotografia revelada em filme de 35mm, grain analógico visível, borda de foto polaroid, "
        "estética de década de 70 ou 80, cores desbotadas pelo envelhecimento químico, "
        "objeto antigo fotografado, memória afetiva, câmera de rolo, revelação manual, retrô documental."
    ),

    
    "Noturno (Festa)": (
        "Multidão dançando em espaço fechado, rostos suados e sorridentes, celebração coletiva, "
        "grupo de pessoas em festa, movimento social e desinibido, ambiente de clube ou balada, "
        "interação entre desconhecidos, euforia compartilhada, noite como evento social, "
        "bebida, música implícita, corpos próximos."
    ),
}
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    output_filepath = os.path.join(project_root, "data/raw/knowledge_anchors.json")
    export_knowledge_anchors_to_json(
        anchors_dict=anchors,
        output_filepath=output_filepath,
        model_name="paraphrase-multilingual-MiniLM-L12-v2"
    )

    
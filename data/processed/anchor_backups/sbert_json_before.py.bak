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
   anchors = anchors = {
    "Vitalidade (Ação)": (
    "foto de esporte com ação e movimento físico intenso. corrida, salto, esforço."
    "atlético, dinâmico, adrenalina, suor, força, intenso. "
    "foto clara, branca, superexposta, lavada de luz, high key, muito brilho, "  # <-- exclusivo
    "estourou de branco, claridade extrema, tudo iluminado, sem sombra. "           # <-- exclusivo
    "cores vibrantes, saturadas, cena com energia e movimento."                    # <-- novo
),
    
    "Solenidade (Estase)": (
        "foto parada e silenciosa. ambiente organizado, limpo e simétrico. "
        "calmo, sereno, tranquilo, neutro, minimalista, equilibrado, suave. "
        "sem bagunça, sem movimento, tudo no lugar, paz visual, elegante e contido."
    ),

    "Conexão (Close-up)": (
        "foto de rosto humano em plano fechado, close extremo, sorriso, olhar direto, expressão emocional. "
        "feliz, alegre, acolhedor, caloroso, amigável, empático, íntimo, carinhoso. "
        "aproximação, afeto, presença humana, emoção no rosto, calor humano."
    ),

    "Distanciamento (Low-key)": (
        "foto escura, sombria e pesada. lugar vazio, abandonado, desolado, concreto. "
        "solitário, isolado, triste, frio, melancólico, silencioso, distante. "
        "sensação de solidão, ninguém por perto, ambiente opressivo, luz baixa e dura."
    ),

    "Simplicidade (Cotidiano)": (
        "foto comum do dia a dia, sem produção. casa, cozinha, rua, trabalho, rotina. "
        "natural, simples, casual, autêntico, doméstico, familiar, sem pose. "
        "luz de janela, cena ordinária, momento espontâneo, vida real sem filtro."
    ),

    "Conflito (Caos)": (
        "foto de confusão e desordem urbana, rua suja e multidão agitada. cena caótica, tensão. "
        "bagunçado, áspero, agressivo, estressante, poluído, urbano e hostil. "
        "sensação de conflito, ambiente carregado, cena pesada, perturbador visualmente."
    ),

    "Nostalgia (Analógico)": (
    "fotografia com cara de antiga, velha, de outro tempo. película, polaroid, filme de 35mm. "
    "cores desbotadas, granulado, retrô, vintage, anos 70, anos 80, anos 90, anos 2000. "
    "saudade, memória, passado, afeto antigo, estética analógica, revelado à mão. "
    "subcultura, emo, punk, gótico, alternativo, indie, rock, banda, show underground. "
    "sensação de nostalgia, saudade, atmosfera de outro tempo, memória afetiva do passado."
),
    
    "Sublime (Paisagem)": (
        "foto de paisagem enorme e impressionante. natureza selvagem, montanha, oceano, céu. "
        "épico, grandioso, majestoso, tirar o fôlego, imensurável, contemplativo. "
        "pessoa pequena perto da natureza, horizonte infinito, pôr do sol dramático, deslumbrante."
    ),

    "Corporativo (Focado)": (
        "foto profissional para currículo, linkedin ou apresentação de trabalho. "
        "sério, confiável, formal, neutro, limpo, estúdio, fundo liso. "
        "imagem de executivo, chefe, funcionário, empresário, headshot, foto de perfil profissional."
    ),

    "Noturno (Festa)": (
        "foto de festa, balada, celebração, evento social à noite. "
        "amigos juntos, dança, euforia, animado, desinibido, multidão feliz. "
        "encontro, bebida, show, rave, clube, farra, agito, turma reunida, comemoração."
    ),
    "__tecnico__": (
        # nomenclatura formal de câmera e óptica
        "abertura, diafragma, f-stop, lente, milímetros, objetiva, focal, zoom, teleobjetiva, "
        "grande angular, fisheye, macro, tilt-shift, prime, kit lens, bokeh, desfoque, "
        "profundidade de campo, rasa, profunda, foco seletivo, foco suave, foco nítido. "

        # exposição e luz técnica
        "exposição, subexposto, superexposto, overexposed, underexposed, high key, low key, "
        "histograma, zebra, clipping, queimado, estourado tecnicamente, recuperar sombras, "
        "recuperar luzes, dynamic range, faixa dinâmica, latitude de exposição. "

        # velocidade e movimento técnico
        "velocidade do obturador, shutter speed, tempo de exposição, congelar movimento, "
        "motion blur, rastro de luz, longa exposição, bulb, 1/1000, 1/500, 1/60, 30 segundos. "

        # sensibilidade e ruído técnico
        "ISO, sensibilidade, ruído digital, grain técnico, noise, redução de ruído, "
        "ISO baixo, ISO alto, ISO nativo, clean ISO, sensor, full frame, crop, APS-C, micro quatro terços. "

        # iluminação de estúdio e equipamento
        "softbox, octobox, beauty dish, refletor, difusor, strobe, flash externo, speedlight, "
        "luz contínua, LED, tungstênio, fluorescente, monolight, pack e cabeça, "
        "luz principal, luz de preenchimento, contraluz, hair light, rim light, "
        "razão de iluminação, Rembrandt, loop, split, butterfly, clamshell. "

        # cor e temperatura técnica
        "temperatura de cor, kelvin, balanço de branco, auto white balance, "
        "luz fria, luz neutra, luz quente, daylight, tungsten, fluorescent, shade, cloudy, "
        "matiz, viragem, LUT, perfil de cor, picture profile, log, flat, S-log, C-log. "

        # pós-processamento e técnica digital
        "raw, dng, jpeg, compressão, edição técnica, lightroom, capture one, darktable, "
        "curva de tons, curva S, máscaras de luminância, dodge and burn, frequência de separação, "
        "skin retouch, healing, clone stamp, redução de ruído técnica, sharpen, unsharp mask. "

        # composição técnica
        "regra dos terços, proporção áurea, linha do horizonte, ponto de fuga, "
        "enquadramento, corte, crop técnico, proporção de aspecto, 16x9, 3x2, 4x5, quadrado. "

        # descrições técnicas em linguagem informal de fotógrafo
        "deixa o fundo borrado, fundo sumiu, fundo sumir, fundo desfocado, desfoca o fundo, "
        "congelar o movimento, capturar o movimento, motion, rastro, blur intencional, "
        "abertura bem aberta, abrir o diafragma, fechar o diafragma, expor para as sombras, "
        "expor para as luzes, segurar as luzes, segurar as sombras, achatar a imagem, "
        "imagem flat, tirar o contraste, forçar o ISO, subir o ISO, estourar o branco tecnicamente."
    ),
}
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
output_filepath = os.path.join(project_root, "data/raw/knowledge_anchors.json")
export_knowledge_anchors_to_json(
        anchors_dict=anchors,
        output_filepath=output_filepath,
        model_name="paraphrase-multilingual-MiniLM-L12-v2"
    )
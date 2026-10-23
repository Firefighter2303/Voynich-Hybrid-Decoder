
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from collections import Counter

class VoynichOrderedDecoder:
    def __init__(self, full_text_corpus):
        self.full_text = full_text_corpus
        
        # 1. Integriertes Renaissance-Wörterbuch
        self.medieval_dict = {
            "ivola": "VIOLA {Pflanze: Stiefmütterchen/Veilchen}",
            "toro": "TORO {Tierkreis: Stier}",
            "aprile": "APRILE {Monat: April}",
            "gemelli": "GEMELLI {Tierkreis: Zwillinge}",
            "maio": "MAIO {Monat: Mai}",
            "ereto": "ARIETE {Tierkreis: Widder}",
            "arieto": "ARIETE {Tierkreis: Widder}",
            "loc": "LOCO {Ort / hier}",
            "loco": "LOCO {Ort / hier}",
            "lo": "LO {Artikel: es / das}",
            "abad": "ABANTE {vorne / vorstehend}",
            "raco": "RACCOGLIERE {pflücken / ernten}",
            "soga": "SFOGA {abfließen / ausleiten}",
            "colo": "COLO {filtern / seihen}",
            "sacaf": "SACCO {Filterbeutel / Sack}",
            "ioqc": "COQUI {kochen / sieden}",
            "icad": "DIECI {Menge: zehn Teile}",
            "alixo": "ALIXO {lindern / erleichtern}",
            "aiut": "AIUTA {hilft / es hilft}",
            "anedlav": "LAVANDA ANETHI {Dill-Wasser / Magen-Waschung}",
            "orario": "ORARIO {Stundeneinteilung / Uhrzeit}",
            "roeto": "RUOTA {Rad / Kreislauf}",
            "doc": "DOC / DUCE {Leitstern / zwölf Stunden}",
            "nidiad": "NIDATA {Ansammlung / Konstellation}",
            "ycad": "DECA {die Dekane / 10-Tage-Einteilung}"
        }
        
        # 2. Wissenschaftlich rekonstruierte Reihenfolge
        self.correct_page_order = {
            "f1r": 1, "f72r": 2, "f86v": 3, "f116v": 4
        }
        
        self.placeholders = self._detect_placeholders()

    def _detect_placeholders(self):
        words = self.full_text.split()
        counts = Counter(words)
        total = len(words) if len(words) > 0 else 1
        dynamic_noise = [w for w, c in counts.items() if (c / total) > 0.05]
        static_noise = ["chckh", "chcly", "kchckh", "chchcy", "ctcly", "kchccy", "chckhh"]
        return set(static_noise + dynamic_noise)

    def decode_line(self, line_text):
        # Bereinigung von Transkript-Tags (wie <f1r.1>)
        if ">" in line_text:
            line_text = line_text.split(">", 1)[1]
            
        words = line_text.replace(".", " ").split()
        decoded_words = []
        
        for w in words:
            w = w.lower().strip("-!,.*<>")
            if not w or w in self.placeholders:
                continue
                
            reversed_w = w[::-1]
            clean_w = reversed_w.replace('y', 'i').replace('h', '')
            
            if not any(vocal in clean_w for vocal in ['a', 'e', 'i', 'o', 'u']):
                continue
                
            if clean_w in self.medieval_dict:
                decoded_words.append(self.medieval_dict[clean_w])
            else:
                decoded_words.append(f"{clean_w}*")
                
        return " ".join(decoded_words)

    def parse_raw_corpus(self, raw_lines_list):
        page_buckets = {}
        
        for line in raw_lines_list:
            current_page = "f1r"
            if line.startswith("<") and ">" in line:
                tag = line.split(">")[0].replace("<", "")
                current_page = tag.split(".")[0]
            
            if current_page not in page_buckets:
                page_buckets[current_page] = []
            page_buckets[current_page].append(line)
            
        sorted_pages = sorted(
            page_buckets.keys(), 
            key=lambda p: self.correct_page_order.get(p, 999)
        )
        
        output_lines = []
        for page in sorted_pages:
            output_lines.append(f"\n--- REKONSTRUIERTE POSITION: SCHRIFTBLATT {page.upper()} ---")
            for line in page_buckets[page]:
                translation = self.decode_line(line)
                if translation.strip():
                    output_lines.append(f"  > {translation}")
                    
        return output_lines

def main():
    input_file = "voynich_text.txt"
    output_file = "voynich_entschluesselt.txt"
    
    if not os.path.exists(input_file):
        print(f"Hinweis: '{input_file}' nicht gefunden. Starte den integrierten Simulator...\n")
        test_corpus = [
            "<f1r.1> alovi chckh shol chcly daba ctcly",
            "<f86v.1> chckh chcly kchckh chol dacy chcly chchcy ctcly",
            "<f72r.1> oioro elirpa chckh oteor",
            "<f116v.1> oxila teia chckh valdena ctcly"
        ]
        
        decoder = VoynichOrderedDecoder("\n".join(test_corpus))
        results = decoder.parse_raw_corpus(test_corpus)
        for res in results:
            print(res)
        return

    print(f"Starte Großfeld-Analyse. Lese '{input_file}' ein...")
    with open(input_file, "r", encoding="utf-8") as f:
        raw_lines = f.readlines()
        
    decoder = VoynichOrderedDecoder("".join(raw_lines))
    ordered_translation = decoder.parse_raw_corpus(raw_lines)
    
    with open(output_file, "w", encoding="utf-8") as out:
        out.write("=== VOYNICH-MANUSKRIPT: CHRONOLOGISCH GEFILTERTER KLARTEXT ===\n\n")
        for line in ordered_translation:
            out.write(line + "\n")
            
    print(f"\n[ERFOLG] Das gesamte Buch wurde neu geordnet und gefiltert.")

if __name__ == "__main__":
    main()

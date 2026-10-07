import os
from pathlib import Path
from core.base_brain import BaseBrain


class MysteryBrain(BaseBrain):
    channel_name = "mystery"

    def _load_prompt(self, prompt_filename):
        """
        Lit le fichier Markdown spécifique à la chaîne.
        Idéalement, cette méthode devrait être dans BaseBrain pour que 
        CapitalSimpleBrain et MimoluneBrain en profitent automatiquement.
        """
        base_dir = Path(__file__).parent.parent  # Ajuste selon l'arborescence exacte
        filepath = base_dir / "channels" / self.channel_name / "prompts" / prompt_filename
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read().strip()
        except FileNotFoundError:
            print(f"⚠️ Fichier prompt introuvable : {filepath}")
            return ""

    def build_script_prompt(self, topic, scene_count, chosen_hook, grounding_block, correction_feedback=""):
        # 1. Chargement des instructions depuis les fichiers .md
        system_msg = self._load_prompt("system.md")
        script_template = self._load_prompt("scripts.md")

        # 2. Remplacement sécurisé des variables (évite .format() si ton Markdown contient des accolades JSON {})
        user_msg = script_template.replace("{topic}", str(topic)) \
                                  .replace("{scene_count}", str(scene_count)) \
                                  .replace("{chosen_hook}", str(chosen_hook)) \
                                  .replace("{grounding_block}", str(grounding_block))

        # 3. Ajout du feedback de correction si c'est un retry (fact-checking échoué)
        if correction_feedback:
            user_msg += f"\n\n{correction_feedback}"

        return [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ]

    def check_script_logic(self, topic, data):
        # Appel du WikidataChecker et du LLM pour le fact-checking
        issues = []
        
        # Exemple d'intégration de ta logique de vérification
        geo_issues = self._check_wikidata_locations(data.get("scenes", []))
        if geo_issues:
            issues.extend(geo_issues)
            
        return issues
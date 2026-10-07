import os
import yaml
from pathlib import Path
from channels.mystery.brain import MysteryBrain
# from services.audio.audio_engine import AudioEngine (à adapter selon tes imports)
# from services.visuals.asset_manager import AssetManager
from services.video.composer import Composer


class VideoPipeline:
    """
    Orchestrateur générique de création de vidéo.
    """
    def __init__(self, channel_name="mystery"):
        self.channel_name = channel_name
        self.config = self._load_channel_config()
        
        # Instanciation des modules avec la configuration injectée
        self.brain = self._init_brain()
        # self.audio_engine = AudioEngine(channel_config=self.config.get("audio", {}))
        # self.asset_manager = AssetManager(channel_config=self.config.get("visuals", {}))
        self.composer = Composer(channel_config=self.config.get("video_composer", {}))

    def _load_channel_config(self):
        """Charge le fichier YAML de la chaîne (ex: config/channels/mystery.yaml)."""
        base_dir = Path(__file__).resolve().parent.parent
        config_path = base_dir / "config" / "channels" / f"{self.channel_name}.yaml"
        
        if not config_path.exists():
            raise FileNotFoundError(f"Fichier de configuration introuvable : {config_path}")
            
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _init_brain(self):
        """Initialise le bon Brain en fonction de la chaîne."""
        if self.channel_name == "mystery":
            return MysteryBrain() # Le brain lit ses propres .md dans channels/mystery/prompts/
        # elif self.channel_name == "finance":
        #    return FinanceBrain()
        else:
            raise ValueError(f"Brain inconnu pour la chaîne : {self.channel_name}")

    def run(self):
        """Exécute le pipeline complet de création."""
        print(f"🚀 Démarrage du pipeline pour la chaîne : {self.channel_name}")
        
        # 1. Génération du sujet
        topic = self.brain.get_trending_topic()
        print(f"📝 Sujet choisi : {topic}")
        
        # 2. Génération du script (le brain s'occupe de lire les .md)
        script_data = self.brain.generate_script(topic)
        print(f"📜 Script généré avec {len(script_data['scenes'])} scènes.")
        
        # --- (Faux code pour l'exemple, à remplacer par tes vrais appels) ---
        # 3. Génération Audio
        # print("🎙️ Génération de l'audio et des sous-titres...")
        # self.audio_engine.generate_for_script(script_data)
        
        # 4. Génération Visuelle
        # print("🖼️ Récupération des médias visuels...")
        # video_pairs = self.asset_manager.fetch_assets_for_script(script_data)
        video_pairs = [] # Remplacer par la vraie liste des chemins d'images/vidéos
        
        # 5. Composition Finale
        print("🎬 Lancement du rendu vidéo...")
        rendered_scenes = self.composer.render_all_scenes(script_data["scenes"], video_pairs)
        final_video_path = self.composer.concatenate_with_transitions(
            rendered_scenes, 
            output_filename=f"{self.channel_name}_final.mp4"
        )
        
        print(f"✅ Vidéo terminée ! Sauvegardée ici : {final_video_path}")
        return final_video_path

# Point d'entrée pour tester rapidement
if __name__ == "__main__":
    pipeline = VideoPipeline(channel_name="mystery")
    pipeline.run()
import json, os, time, platform, subprocess, sys
from gtts import gTTS
from core_engine.moment_integration import log_mostar_moment

class MostarVoice:
    def __init__(self, lingua="yoruba", lang_code="yo"):
        self.lingua = lingua.lower()
        self.lang_code = lang_code
        self.registry = self._load_voice_manifest()
        self.voice_cache_dirs = [
            os.path.join("data", "voice_cache"),
            os.path.join("backend", "data", "voice_cache")
        ]
        print(f"🔊 MostarVoice initialized :: {self.lingua.upper()} [{self.lang_code}]")

    def _load_voice_manifest(self):
        manifest_path = os.path.join("core_engine", "voice_manifest.json")
        if os.path.exists(manifest_path):
            with open(manifest_path, "r", encoding="utf-8") as f:
                return json.load(f)
        print("⚠️ No voice_manifest.json found — using default fallback only.")
        return {}

    def _find_voice_clip(self, key):
        lang_manifest = self.registry.get(self.lingua, {})
        filename = lang_manifest.get(key) or lang_manifest.get("fallback")
        if not filename:
            return None

        for cache_dir in self.voice_cache_dirs:
            file_path = os.path.join(cache_dir, filename)
            if os.path.exists(file_path):
                return os.path.abspath(file_path)
        return None

    def _play_audio(self, file_path):
        """Cross-platform audio playback"""
        try:
            system = platform.system().lower()
            if system == "windows":
                # Use default associated player
                os.startfile(file_path)
            elif system == "darwin":
                subprocess.call(["open", file_path])
            else:  # linux
                subprocess.call(["xdg-open", file_path])
            print(f"🎧 Playback initiated -> {file_path}")
        except Exception as e:
            print(f"⚠️ Audio playback failed: {e}")

    def speak(self, text, phrase_key=None):
        file_path = self._find_voice_clip(phrase_key or "fallback")
        filename = f"voice_{int(time.time())}.mp3"

        if file_path:
            self._play_audio(file_path)
            print(f"🎧 Played contextual voice: {phrase_key or 'fallback'}")
            log_mostar_moment(
                initiator="Voice Layer",
                receiver="Soul Layer",
                description=f"Played contextual voice for '{phrase_key or 'fallback'}'",
                trigger_type="voice",
                resonance_score=0.96
            )
        else:
            try:
                tts = gTTS(text=text, lang=self.lang_code)
                save_path = os.path.join("data", "voice_cache", filename)
                tts.save(save_path)
                self._play_audio(save_path)
                print(f"🎧 Synthesized speech for '{phrase_key}'")
            except Exception as e:
                print(f"⚠️ Voice synthesis failed: {e}")

if __name__ == "__main__":
    mv = MostarVoice("yoruba", "yo")
    mv.speak("MoStar AI ti ji, o n sọ̀rọ̀ loni — pẹlu ọrọ ati àṣẹ.", "seal_covenant")
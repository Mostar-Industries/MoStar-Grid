import json, os, time, platform, subprocess
from gtts import gTTS
from core_engine.moment_integration import log_mostar_moment

class MostarVoice:
    _LANG_ALIASES = {
        "yo": ("yoruba", "yo"),
        "yoruba": ("yoruba", "yo"),
        "en": ("english", "en"),
        "english": ("english", "en"),
        "sw": ("swahili", "sw"),
        "swahili": ("swahili", "sw"),
    }

    def __init__(self, lingua=None, lang_code=None, lang=None):
        self.lingua, self.lang_code = self._normalize_language_inputs(
            lingua=lingua,
            lang_code=lang_code,
            lang=lang,
        )
        self.registry = self._load_voice_manifest()
        self.voice_cache_dirs = [
            os.path.join("data", "voice_cache"),
            os.path.join("backend", "data", "voice_cache")
        ]
        for cache_dir in self.voice_cache_dirs:
            os.makedirs(cache_dir, exist_ok=True)
        print(f"🔊 MostarVoice initialized :: {self.lingua.upper()} [{self.lang_code}]")

    def _normalize_language_inputs(self, lingua, lang_code, lang):
        if lang:
            return self._resolve_alias(lang, fallback_code=lang_code)

        if lingua:
            return self._resolve_alias(lingua, fallback_code=lang_code)

        if lang_code:
            return self._resolve_alias(lang_code, fallback_code=lang_code)

        return self._LANG_ALIASES["yoruba"]

    def _resolve_alias(self, key, fallback_code=None):
        key_lower = key.lower()
        normalized = self._LANG_ALIASES.get(key_lower)

        if normalized:
            lingua_value, code_value = normalized
        else:
            lingua_value = key_lower
            code_value = key_lower

        if fallback_code:
            code_value = fallback_code.lower()

        return lingua_value, code_value

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

import { getAudioContext, decodeAudioData } from "@/lib/sound-engine";
import type {
  SoundAsset,
  UseSoundOptions,
  UseSoundReturn,
  PlayFunction,
  SoundControls,
} from "@/lib/sound-types";

export function useSound(
  sound: SoundAsset,
  options: UseSoundOptions = {}
): UseSoundReturn {
  const {
    volume = 1,
    playbackRate = 1,
    interrupt = false,
    soundEnabled = true,
    onPlay,
    onEnd,
    onPause,
    onStop,
  } = options;

  let isPlaying = false;
  let duration: number | null = sound.duration ?? null;
  let sourceNode: AudioBufferSourceNode | null = null;
  let cachedBuffer: AudioBuffer | null = null;

  // Immediately decode audio buffer into memory on instantiation
  if (typeof window !== "undefined" && sound?.dataUri) {
    decodeAudioData(sound.dataUri)
      .then((buf) => {
        cachedBuffer = buf;
        duration = buf.duration;
      })
      .catch(() => {});
  }

  const stop = () => {
    if (sourceNode) {
      try {
        sourceNode.stop();
      } catch {}
      sourceNode = null;
    }
    isPlaying = false;
    onStop?.();
  };

  const pause = () => {
    stop();
    onPause?.();
  };

  const play: PlayFunction = (overrides?: {
    volume?: number;
    playbackRate?: number;
  }) => {
    if (!soundEnabled) return;

    const playVolume = overrides?.volume ?? volume;
    const playRate = overrides?.playbackRate ?? playbackRate;

    try {
      const ctx = getAudioContext();
      // Resume audio context immediately if suspended (no await!)
      if (ctx.state === "suspended") {
        ctx.resume();
      }

      if (interrupt && sourceNode) {
        stop();
      }

      const executePlay = (buf: AudioBuffer) => {
        const source = ctx.createBufferSource();
        const gain = ctx.createGain();

        source.buffer = buf;
        source.playbackRate.value = playRate;
        gain.gain.value = playVolume;

        source.connect(gain);
        gain.connect(ctx.destination);

        source.onended = () => {
          isPlaying = false;
          onEnd?.();
        };

        source.start(0); // 0ms instant start
        sourceNode = source;
        isPlaying = true;
        onPlay?.();
      };

      if (cachedBuffer) {
        // Synchronous 0ms playback
        executePlay(cachedBuffer);
      } else {
        decodeAudioData(sound.dataUri)
          .then((buf) => {
            cachedBuffer = buf;
            duration = buf.duration;
            executePlay(buf);
          })
          .catch(() => {
            try {
              const audio = new Audio(sound.dataUri);
              audio.volume = Math.max(0, Math.min(1, playVolume));
              audio.playbackRate = playRate;
              audio.play().catch(() => {});
            } catch {}
          });
      }
    } catch {
      try {
        const audio = new Audio(sound.dataUri);
        audio.volume = Math.max(0, Math.min(1, playVolume));
        audio.playbackRate = playRate;
        audio.play().catch(() => {});
      } catch {}
    }
  };

  const controls: SoundControls = {
    stop,
    pause,
    get isPlaying() {
      return isPlaying;
    },
    get duration() {
      return duration;
    },
    sound,
  };

  const result = [play, controls] as unknown as UseSoundReturn & {
    play: PlayFunction;
    stop: () => void;
    pause: () => void;
    isPlaying: boolean;
  };
  result.play = play;
  result.stop = stop;
  result.pause = pause;

  return result as UseSoundReturn;
}

export default useSound;

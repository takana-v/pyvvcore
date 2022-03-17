import faulthandler
import json
from ctypes import CDLL, c_bool, c_char_p, c_int, c_uint8, pointer
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .core import VVCore


class VVTTSLib:
    """
    VOICEVOX C++音声合成ライブラリのラッパーです。
    """

    def __init__(
        self,
        ttslib_path: Union[str, Path],
        use_gpu: bool = False,
        cpu_num_threads: int = 0,
        dict_dir: Optional[Union[str, Path]] = None,
        init_dir: Optional[Union[str, Path]] = None,
        ort_path: Optional[Union[str, Path]] = None,
        enable_faulthandler: bool = True,
    ):
        """
        クラスの初期化を行います。

        Parameters
        ----------
        ttslib_path: str or pathlib.Path
            VOICEVOXのTTSライブラリのパスを指定します。
        use_gpu: bool, default False
            GPUを使用する場合はTrue、CPUを使用する場合はFalseを指定します。
        cpu_num_threads: int, default 0
            推論に用いるスレッド数を指定します。
            0の場合、論理コア数の半分か、物理コア数が設定されます。
        dict_dir: str or pathlib.Path, optional
            OpenJTalkが使用する辞書があるディレクトリのパスを指定します。
            指定が無い場合、OpenJTalkの初期化は行われません。
        init_dir: str or pathlib.Path, optional
            コアの初期化を行う際のディレクトリのパスを指定します。
            指定が無い場合、cpplib_pathのディレクトリが代わりに使用されます。
        ort_path: str or pathlib.Path, optional
            Onnx Runtimeのパスを指定します。
            指定した場合、指定されたライブラリをプリロードします。
        enable_faulthandler: bool, default True
            Trueの場合、フォールトハンドラを有効にします。
        """
        if ort_path is not None:
            if isinstance(ort_path, str):
                ort_path = Path(ort_path)
            ort_path.expanduser().resolve(strict=True)
            CDLL(str(ort_path))

        if isinstance(ttslib_path, str):
            ttslib_path = Path(ttslib_path)
        ttslib_path.expanduser().resolve(strict=True)

        if init_dir is None:
            init_dir = ttslib_path.parent
        elif isinstance(init_dir, str):
            init_dir = Path(init_dir)
        init_dir.expanduser().resolve(strict=True)

        if enable_faulthandler:
            if not faulthandler.is_enabled():
                faulthandler.enable()
        self.core = VVCore(CDLL(str(ttslib_path)))
        init_res = self.core.initialize(
            root_dir_path=str(init_dir).encode(encoding="utf-8"),
            use_gpu=c_bool(use_gpu),
            cpu_num_threads=cpu_num_threads,
        )

        if not init_res:
            raise RuntimeError(
                "コアの初期化に失敗しました。\n"
                + self.core.last_error_message().decode(encoding="utf-8")
            )

        if dict_dir is not None:
            if isinstance(dict_dir, str):
                dict_dir = Path(dict_dir)
            dict_dir.expanduser().resolve(True)
            init_ojt_res = self.core.voicevox_initialize_openjtalk(
                c_char_p(str(dict_dir).encode(encoding="utf-8"))
            )
            if init_ojt_res != 0:
                raise RuntimeError(
                    "Open JTalkの初期化に失敗しました。\n"
                    + self.core.voicevox_error_result_to_message(init_ojt_res).decode(
                        encoding="utf-8"
                    )
                )

    def tts(self, text: str, speaker_id: int) -> bytes:
        """
        音声合成を行います。

        Parameters
        ----------
        text: str
            音声合成を行う文章を指定します。
        speaker_id: int
            音声合成を行う話者のspeaker_idを指定します。
            metas関数で確認可能です。

        Returns
        -------
        bytes
            wav形式の音声データです。
        """
        output_binary_size = pointer(c_int())
        output_wav = pointer(pointer(c_uint8()))
        _tts_res = self.core.voicevox_tts(
            text.encode(encoding="utf-8"), speaker_id, output_binary_size, output_wav
        )
        if _tts_res != 0:
            self.core.voicevox_wav_free(output_wav.contents)
            raise RuntimeError(
                "音声合成に失敗しました。\n"
                + self.core.voicevox_error_result_to_message(_tts_res).decode(
                    encoding="utf-8"
                )
            )
        _ret_binary_data = b""
        for i in range(output_binary_size.contents.value):
            _ret_binary_data += bytes.fromhex(hex(output_wav.contents[i])[2:].zfill(2))
        self.core.voicevox_wav_free(output_wav.contents)
        return _ret_binary_data

    def metas(self) -> List[Dict[str, Any]]:
        """
        コアが提供するmetas情報を取得します。

        Returns
        -------
        dict
            コアが提供するmetas情報です。
        """
        return json.loads(self.core.metas().decode(encoding="utf-8"))

    def supported_devices(self) -> Dict[str, bool]:
        """
        コアが提供するsupported_devices情報を取得します。

        Returns
        -------
        dict
            コアが提供するsupported_devices情報です。
        """
        return json.loads(self.core.supported_devices().decode(encoding="utf-8"))

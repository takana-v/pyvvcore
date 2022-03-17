from ctypes import (
    CDLL,
    POINTER,
    c_bool,
    c_char_p,
    c_float,
    c_int,
    c_int64,
    c_uint8,
    pointer,
)
from typing import Union


class VVCore:
    """
    VOICEVOX Core（C++音声合成ライブラリを含む）のラッパーです。
    """

    def __init__(self, core: CDLL):
        """
        クラスを初期化します。

        Parameters
        ----------
        core: ctypes.CDLL
            VOICEVOX C++ ライブラリのインスタンスを指定します。
        """
        self.core = core
        self.core.initialize.argtypes = [c_char_p, c_bool, c_int]
        self.core.initialize.restype = c_bool
        self.core.finalize.argtypes = []
        self.core.finalize.restype = None
        self.core.metas.argtypes = []
        self.core.metas.restype = c_char_p
        self.core.supported_devices.argtypes = []
        self.core.supported_devices.restype = c_char_p
        self.core.yukarin_s_forward.argtypes = [
            c_int64,
            POINTER(c_int64),
            POINTER(c_int64),
            POINTER(c_float),
        ]
        self.core.yukarin_s_forward.restype = c_bool
        self.core.yukarin_sa_forward.argtypes = [
            c_int64,
            POINTER(c_int64),
            POINTER(c_int64),
            POINTER(c_int64),
            POINTER(c_int64),
            POINTER(c_int64),
            POINTER(c_int64),
            POINTER(c_int64),
            POINTER(c_float),
        ]
        self.core.yukarin_sa_forward.restype = c_bool
        self.core.decode_forward.argtypes = [
            c_int64,
            c_int64,
            POINTER(c_float),
            POINTER(c_float),
            POINTER(c_int64),
            POINTER(c_float),
        ]
        self.core.last_error_message.argtypes = []
        self.core.last_error_message.restype = c_char_p
        self.core.voicevox_initialize_openjtalk.argtypes = [c_char_p]
        self.core.voicevox_initialize_openjtalk.restype = c_int
        self.core.voicevox_tts.argtypes = [
            c_char_p,
            c_int64,
            POINTER(c_int),
            POINTER(POINTER(c_uint8)),
        ]
        self.core.voicevox_tts.restype = c_int
        self.core.voicevox_wav_free.argtypes = [POINTER(c_uint8)]
        self.core.voicevox_wav_free.restype = None
        self.core.voicevox_error_result_to_message.argtypes = [c_int]
        self.core.voicevox_error_result_to_message.restype = c_char_p

    def initialize(
        self,
        root_dir_path: Union[bytes, c_char_p],
        use_gpu: c_bool,
        cpu_num_threads: Union[int, c_int] = 0,
    ) -> bool:
        """
        コアを初期化します。

        Parameters
        ----------
        root_dir_path: bytes or ctypes.c_char_p
            必要なファイルがあるディレクトリを指定します。
            相対パス、絶対パスの両方が指定可能です。
        use_gpu: ctypes.c_bool
            TrueならGPU用の初期化、FalseならCPU用の初期化を行います。
        cpu_num_threads: int or ctypes.c_int, default 0
            推論に用いるスレッド数を指定します。
            0の場合、論理コア数の半分か、物理コア数が設定されます。

        Returns
        -------
        bool
            成功したらTrue、失敗したらFalseが返されます。
        """
        return self.core.initialize(root_dir_path, use_gpu, cpu_num_threads)

    def finalize(self) -> None:
        """
        終了処理を行います。
        以降関数を使用するためには再度初期化を行う必要があります。
        何度も実行可能です。

        Warnings
        --------
        CUDAを使用している場合、この関数を実行しておかないと例外が起こることがあります。
        """
        return self.core.finalize()

    def metas(self) -> bytes:
        """
        メタ情報を取得します。

        Returns
        -------
        bytes
            メタ情報が格納されたjson形式の文字列です。
        """
        return self.core.metas()

    def supported_devices(self) -> bytes:
        """
        対応デバイス情報を取得します。
        cpu、cudaのうち、使用可能なデバイスの情報です。

        Returns
        -------
        bytes
            各デバイスが使用可能かをboolで格納したjson形式の文字列です。
        """
        return self.core.supported_devices()

    def yukarin_s_forward(
        self,
        length: Union[int, c_int64],
        phoneme_list: pointer,
        speaker_id: pointer,
        output: pointer,
    ) -> bool:
        """
        音素列から音素ごとの長さを求めます。

        Parameters
        ----------
        length: int or ctypes.c_int64
            モーラ列の長さを指定します。
        phoneme_list: ctypes.pointer
            音素列を指定します。
            正確な型はctypes.POINTER(ctypes.c_int64)の返り値です。
        speaker_id: ctypes.pointer
            話者番号を指定します。
            正確な型はctypes.POINTER(ctypes.c_int64)の返り値です。
        output: ctypes.pointer
            音素ごとの長さを出力する先のポインタを指定します。
            正確な型はctypes.POINTER(ctypes.c_float)の返り値です。

        Returns
        -------
        bool
            成功したらTrue、失敗したらFalseが返されます。
        """
        return self.core.yukarin_s_forward(length, phoneme_list, speaker_id, output)

    def yukarin_sa_forward(
        self,
        length: Union[int, c_int64],
        vowel_phoneme_list: pointer,
        consonant_phoneme_list: pointer,
        start_accent_list: pointer,
        end_accent_list: pointer,
        start_accent_phrase_list: pointer,
        end_accent_phrase_list: pointer,
        speaker_id: pointer,
        output: pointer,
    ) -> bool:
        """
        モーラごとの音素列とアクセント情報からモーラごとの音高を求めます。

        Parameters
        ----------
        length: int or c_int64
            モーラ列の長さを指定します。
        vowel_phoneme_list: ctypes.pointer
            母音の音素列を指定します。
            正確な型はctypes.POINTER(ctypes.c_int64)の返り値です。
        consonant_phoneme_list: ctypes.pointer
            子音の音素列を指定します。
            正確な型はctypes.POINTER(ctypes.c_int64)の返り値です。
        start_accent_list: ctypes.pointer
            アクセントの開始位置を指定します。
            正確な型はctypes.POINTER(ctypes.c_int64)の返り値です。
        end_accent_list: ctypes.pointer
            アクセントの終了位置を指定します。
            正確な型はctypes.POINTER(ctypes.c_int64)の返り値です。
        start_accent_phrase_list: ctypes.pointer
            アクセント句の開始位置を指定します。
            正確な型はctypes.POINTER(ctypes.c_int64)の返り値です。
        end_accent_phrase_list: ctypes.pointer
            アクセント句の終了位置を指定します。
            正確な型はctypes.POINTER(ctypes.c_int64)の返り値です。
        speaker_id: ctypes.pointer
            話者番号を指定します。
            正確な型はctypes.POINTER(ctypes.c_int64)の返り値です。
        output: ctypes.pointer
            モーラごとの音高を出力する先のポインタを指定します。
            正確な型はctypes.POINTER(ctypes.c_float)の返り値です。

        Returns
        -------
        bool
            成功したらTrue、失敗したらFalseが返されます。
        """
        return self.core.yukarin_sa_forward(
            length,
            vowel_phoneme_list,
            consonant_phoneme_list,
            start_accent_list,
            end_accent_list,
            start_accent_phrase_list,
            end_accent_phrase_list,
            speaker_id,
            output,
        )

    def decode_forward(
        self,
        length: Union[int, c_int64],
        phoneme_size: Union[int, c_int64],
        f0: pointer,
        phoneme: pointer,
        speaker_id: pointer,
        output: pointer,
    ) -> bool:
        """
        フレームごとの音素と音高から波形を求めます。

        Parameters
        ----------
        length: int or ctypes.c_int64
            フレームの長さを指定します。
        phoneme_size: int or ctypes.c_int64
            音素の種類数を指定します。
            正確な型はctypes.POINTER(ctypes.c_float)の返り値です。
        f0: ctypes.pointer
            フレームごとの音高を指定します。
            正確な型はctypes.POINTER(ctypes.c_float)の返り値です。
        phoneme: ctypes.pointer
            フレームごとの音素を指定します。
            正確な型はctypes.POINTER(ctypes.c_float)の返り値です。
        speaker_id: ctypes.pointer
            話者番号を指定します。
            正確な型はctypes.POINTER(ctypes.c_int64)の返り値です。
        output: ctypes.pointer
            波形を出力する先のポインタを指定します。
            正確な型はctypes.POINTER(ctypes.c_float)の返り値です。

        Returns
        -------
        bool
            成功したらTrue、失敗したらFalseが返されます。
        """
        return self.core.decode_forward(
            length, phoneme_size, f0, phoneme, speaker_id, output
        )

    def last_error_message(self) -> bytes:
        """
        最後に発生したエラーのメッセージを取得します。

        Returns
        -------
        bytes
            発生したエラーのメッセージです。
        """
        return self.core.last_error_message()

    def voicevox_initialize_openjtalk(self, dict_path: Union[bytes, c_char_p]) -> int:
        """
        Open JTalkを初期化します。

        Parameters
        ----------
        dict_path: bytes or ctypes.c_char_p
            Open JTalkが使用する辞書のフォルダを指定します。

        Returns
        -------
        int
            結果コードです。
            voicevox_error_result_to_message関数で詳細を得ることができます。
        """
        return self.core.voicevox_initialize_openjtalk(dict_path)

    def voicevox_tts(
        self,
        text: Union[bytes, c_char_p],
        speaker_id: Union[int, c_int64],
        output_binary_size: pointer,
        output_wav: pointer,
    ) -> int:
        """
        Text To Speechを実行します。

        Parameters
        ----------
        text: bytes or ctypes.c_char_p
            音声に変換する文字列を指定します。
        speaker_id: int or ctypes.c_int64
            話者番号を指定します。
        output_binary_size: ctypes.pointer
            音声データのサイズを出力する先のポインタを指定します。
            正確な型はctypes.POINTER(ctypes.c_int)の返り値です。
        output_wav: ctypes.pointer
            音声データを出力する先のポインタを指定します。
            使用が終わったらvoicevox_wav_free関数で開放する必要があります。
            正確な型はctypes.POINTER(ctypes.POINTER(ctypes.c_uint8))の返り値です。

        Returns
        -------
        int
            結果コードです。
            voicevox_error_result_to_message関数で詳細を得ることができます。
        """
        return self.core.voicevox_tts(text, speaker_id, output_binary_size, output_wav)

    def voicevox_wav_free(self, wav: pointer) -> None:
        """
        voicevox_tts関数で生成した音声データを開放します。

        Parameters
        ----------
        wav: ctypes.pointer
            開放する音声データのポインタを指定します。
            正確な型はctypes.POINTER(ctypes.c_uint8)の返り値です。
        """
        return self.core.voicevox_wav_free(wav)

    def voicevox_error_result_to_message(self, result_code: Union[int, c_int]) -> bytes:
        """
        エラーで返ってきた結果コードをメッセージに変換します。

        Parameters
        ----------
        result_code: int or ctypes.c_int
            詳細を表示する結果コードを指定します。

        Returns
        -------
        bytes
            エラーメッセージの文字列です。
        """
        return self.core.voicevox_error_result_to_message(result_code)

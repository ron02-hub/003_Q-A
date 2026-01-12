"""
データ管理モジュール
"""
import json
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd


class DataManager:
    """データの保存・読み込みを管理するクラス"""
    
    def __init__(self, data_dir: Path):
        """
        データマネージャーの初期化
        
        Args:
            data_dir: データ保存ディレクトリ
        """
        self.data_dir = Path(data_dir)
        self.responses_dir = self.data_dir / "responses"
        self.exports_dir = self.data_dir / "exports"
        
        # ディレクトリ作成
        self.responses_dir.mkdir(parents=True, exist_ok=True)
        self.exports_dir.mkdir(parents=True, exist_ok=True)
    
    def save_responses_json(self, session_id: str, responses: Dict[str, Any]) -> Path:
        """
        回答データをJSONファイルに保存
        
        Args:
            session_id: セッションID
            responses: 回答データ
            
        Returns:
            保存したファイルのパス
        """
        filename = f"{session_id}.json"
        filepath = self.responses_dir / filename
        
        data = {
            "session_id": session_id,
            "saved_at": datetime.now().isoformat(),
            "responses": responses,
        }
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return filepath
    
    def load_responses_json(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        JSONファイルから回答データを読み込み
        
        Args:
            session_id: セッションID
            
        Returns:
            回答データ（存在しない場合はNone）
        """
        filename = f"{session_id}.json"
        filepath = self.responses_dir / filename
        
        if not filepath.exists():
            return None
        
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def get_all_responses(self) -> List[Dict[str, Any]]:
        """
        全ての回答データを取得
        
        Returns:
            全回答データのリスト
        """
        responses = []
        for filepath in self.responses_dir.glob("*.json"):
            with open(filepath, "r", encoding="utf-8") as f:
                responses.append(json.load(f))
        return responses
    
    def export_to_csv(self, output_filename: Optional[str] = None) -> Path:
        """
        全回答データをCSVファイルにエクスポート
        
        Args:
            output_filename: 出力ファイル名（指定しない場合は日時で生成）
            
        Returns:
            出力ファイルのパス
        """
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"responses_{timestamp}.csv"
        
        filepath = self.exports_dir / output_filename
        
        all_responses = self.get_all_responses()
        if not all_responses:
            # 空のCSVを作成
            with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["session_id", "saved_at", "responses"])
            return filepath
        
        # データをフラット化
        flattened_data = []
        for response in all_responses:
            flat_row = self._flatten_dict(response)
            flattened_data.append(flat_row)
        
        # DataFrameに変換してCSV出力
        df = pd.DataFrame(flattened_data)
        df.to_csv(filepath, index=False, encoding="utf-8-sig")
        
        return filepath
    
    def export_to_excel(self, output_filename: Optional[str] = None) -> Path:
        """
        全回答データをExcelファイルにエクスポート
        
        Args:
            output_filename: 出力ファイル名（指定しない場合は日時で生成）
            
        Returns:
            出力ファイルのパス
        """
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"responses_{timestamp}.xlsx"
        
        filepath = self.exports_dir / output_filename
        
        all_responses = self.get_all_responses()
        if not all_responses:
            # 空のExcelを作成
            pd.DataFrame().to_excel(filepath, index=False)
            return filepath
        
        # データをフラット化
        flattened_data = []
        for response in all_responses:
            flat_row = self._flatten_dict(response)
            flattened_data.append(flat_row)
        
        # DataFrameに変換してExcel出力
        df = pd.DataFrame(flattened_data)
        
        with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="回答データ", index=False)
            
            # SD法スコアのみを別シートに
            sd_columns = [col for col in df.columns if "sd_" in col.lower()]
            if sd_columns:
                sd_df = df[["session_id"] + sd_columns]
                sd_df.to_excel(writer, sheet_name="SD法評価", index=False)
        
        return filepath
    
    def _flatten_dict(self, d: Dict[str, Any], parent_key: str = "", sep: str = "_") -> Dict[str, Any]:
        """
        ネストされた辞書をフラット化
        
        Args:
            d: フラット化する辞書
            parent_key: 親キー
            sep: キーの区切り文字
            
        Returns:
            フラット化された辞書
        """
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep).items())
            elif isinstance(v, list):
                # リストはJSON文字列として保存
                items.append((new_key, json.dumps(v, ensure_ascii=False)))
            else:
                items.append((new_key, v))
        return dict(items)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        統計データを取得
        
        Returns:
            統計データ
        """
        all_responses = self.get_all_responses()
        
        if not all_responses:
            return {
                "total_responses": 0,
                "completed_responses": 0,
                "group_a_count": 0,
                "group_b_count": 0,
            }
        
        df = pd.DataFrame([self._flatten_dict(r) for r in all_responses])
        
        return {
            "total_responses": len(all_responses),
            "completed_responses": df.get("responses_completed_at", pd.Series()).notna().sum(),
            "group_a_count": (df.get("responses_group", pd.Series()) == "A").sum(),
            "group_b_count": (df.get("responses_group", pd.Series()) == "B").sum(),
        }

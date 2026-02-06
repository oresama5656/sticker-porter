# Sticker Porter - フォルダ整理ツール

LINEスタンプ作成フローにおける「ファイルの仕分け作業」を自動化するツールです。

## 📦 使い方

### 1. 準備
`folder_sorter.py`（または`StickerPorter.exe`）を好きな場所に置いてください。  
初回起動時に、同じ場所に以下のフォルダが自動で作成されます：

| フォルダ名 | 用途 |
|-----------|------|
| `00_WorkBench` | 作業用フォルダ。完成したZIPと生画像フォルダを入れる |
| `01_Ready_To_Upload` | アップロード待ちのZIPを保管 |
| `02_Uploaded_Done` | アップロード済みZIPの保管場所 |
| `99_Raw_Archive` | 生画像フォルダのアーカイブ |

### 2. ワークフロー

#### ステップA: 製造完了時
1. 完成した `.zip` ファイルと生画像フォルダを `00_WorkBench` に入れる
2. ツールを起動して **「📦 製造完了（仕分け）」** ボタンを押す
3. 自動で仕分けが行われます：
   - `.zip` → `01_Ready_To_Upload` へ移動
   - フォルダ → `99_Raw_Archive` へ移動

#### ステップB: 投稿完了時
1. LINEにスタンプを投稿し終わったら
2. **「🚀 投稿完了（片付け）」** ボタンを押す
3. `01_Ready_To_Upload` のZIPが `02_Uploaded_Done` へ移動します

## ⚙️ 設定のカスタマイズ

`config.json` をメモ帳で編集すれば、フォルダ名を変更できます。

```json
{
  "workbench_folder": "00_WorkBench",
  "ready_to_upload_folder": "01_Ready_To_Upload",
  "uploaded_done_folder": "02_Uploaded_Done",
  "raw_archive_folder": "99_Raw_Archive"
}
```

## 🔧 EXE化する方法（配布したい場合）

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "StickerPorter" folder_sorter.py
```

`dist`フォルダに`StickerPorter.exe`が生成されます。

## ❓ トラブルシューティング

| 問題 | 解決策 |
|------|--------|
| フォルダが作成されない | アプリの場所に書き込み権限があるか確認 |
| ファイルが移動されない | ファイルが別のアプリで開かれていないか確認 |
| 同名ファイルがある | 自動でタイムスタンプが付くので心配なし！ |

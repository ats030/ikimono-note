# 実行経路と収録範囲

## ローカルで動かせる部分

[main.py](../main.py)が画面とAPIを提供し、[pipeline.py](../pipeline.py)と[vision.py](../vision.py)が画像処理、AI要求、候補の確認を担います。
記録の正本はブラウザのIndexedDBです。
Google Drive保存は利用者が追加で接続する経路で、Googleへのログインだけで自動的に同期される仕組みではありません。

この公開版の起動スクリプトは、ブラウザ側のWorker用画像処理を無効にしています。
JPEGやHEICの読込みはPython側の実装を使います。
Pythonでの画像処理とWorker用のブラウザ処理を、同じ経路として扱わないようにしています。

## Cloudflare版を読む場所

| ファイル | 読める責務 |
| --- | --- |
| [edge.mjs](../cloudflare-preview/edge.mjs) | 入口、認証、ルーティング、サービスへの接続 |
| [gemini-handler.mjs](../cloudflare-preview/gemini-handler.mjs) | Gemini要求と応答の扱い |
| [gemini-core.mjs](../cloudflare-preview/gemini-core.mjs) | 入力の確認、要求の構築、候補の処理 |
| [gemini-policy.py](../cloudflare-preview/gemini-policy.py) | Python側の定数からJavaScriptの方針データを生成 |
| [src/worker.py](../cloudflare-preview/src/worker.py) | PythonアプリのWorkerへの接続 |
| [d1_store.py](../d1_store.py) | D1へ保存するアカウントや共有情報の操作 |

これらは構成を読むための参考ソースです。
生成済みの方針ファイル、ブラウザ用画像ライブラリ、配備設定、サービスの接続、D1の配備用スキーマを収録していないため、この公開版からWorkerへ直接配備する手順は提供していません。
`gemini-policy.py` による方針データの生成はローカルで確認できますが、生成だけでWorkerの配備が完成するわけではありません。

## 元のアプリとの差分

元のアプリのコミット済みファイルを、履歴を引き継がずに収録しました。
運用の設定、クラウド資源のID、個人のデータ、評価用の外部写真、未コミットの変更はコピーしていません。
Android補助アプリの既存公開バイナリは、そのソースとともに収録しています。

公開用の変更は、ローカル環境で検証する `pillow-heif` の版の固定と、終了したプライベートな設定画面へのリンクを公開アプリの設定画面へ置き換える変更です。
既存テストのリンク期待値も合わせています。
[source-manifest.json](source-manifest.json)に元のファイルのハッシュと変更理由を記録しています。
元のアプリと本番環境には、この公開版の変更を反映していません。

既存テストが参照するDockerfile、評価スクリプト、画面検査の補助スクリプトも収録しています。
Dockerイメージのビルドと外部写真を使う精度評価は今回実行していません。
それらのファイルにある過去の運用説明や計測値は、今回の公開検証の結果ではありません。
通常のローカル起動と画面撮影には、READMEで案内する `scripts/` の隔離した手順を使います。

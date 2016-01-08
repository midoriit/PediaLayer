# PediaLayer
レイヤで指定した範囲内の事物に関するウィキペディアの情報をDBpedia Japaneseから取得するQGISプラグインです。

### インストール
QGISの「プラグイン」メニューから「プラグインの管理とインストール…」を選択し、「設定」タブでプラグインリポジトリに
```
http://midoriit.com/qgis/plugins.xml
```
を追加してから、「全ての」タブで「PediaLayer」をインストールします。

### 使用方法
QGISの「Web」メニューに追加された「Pedia Layer」→「DBpediaからレイヤを作成」を選択すると、ダイアログボックスが表示されます。

![ダイアログボックス](http://midoriit.com/images/2016/01/PediaLayer1.png)

情報を取得する範囲をマップキャンパスまたはレイヤから選択し、［OK］ボタンをクリックすると、DBpediaから取得した情報がマップキャンパスに表示されます。

![結果表示](http://midoriit.com/images/2016/01/PediaLayer2.png)

記事のタイトル（name）、ウィキペディア該当記事のURL（url）、概要説明（abstract）が属性に入ります。

![属性テーブル](http://midoriit.com/images/2016/01/PediaLayer3.png)

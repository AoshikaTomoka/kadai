import flet as ft
import requests

# API URL
URL = "http://www.jma.go.jp/bosai/common/const/area.json"

#ダークモードとライトモードに対応
#ダークモードの場合は色を反転

def main(page: ft.Page):
    page.title = "天気予報"
    page.scroll = "auto"  # スクロール対応

    # 天気予報というタイトルを表示
    page.add(ft.Text("天気予報", size=30, weight="bold", color=ft.colors.BLUE_900))
    page.add(ft.Text("天気予報の地域情報", size=20))

    try:
        # JSONデータの取得
        response = requests.get(URL)
        response.raise_for_status()  # HTTPエラーをチェック
        data_json = response.json()

        # 地域データを取得
        centers = data_json.get("centers", {})

        # 表示を初期化
        def show_region_details(center_id):
            # 選択された地域の詳細を表示
            region_info = centers.get(center_id, {})
            name = region_info.get("name", "不明")
            en_name = region_info.get("enName", "不明")
            office_name = region_info.get("officeName", "不明")
            children = region_info.get("children", [])

            # 詳細情報を表示
            details_section.controls = [
                ft.Text(f"地域 ID: {center_id}", weight="bold", size=18),
                ft.Text(f"地域名 (JP): {name}"),
                ft.Text(f"地域名 (EN): {en_name}"),
                ft.Text(f"気象台: {office_name}"),
                ft.Text(f"子地域 IDs: {', '.join(children)}"),
            ]
            page.update()

        # 地域リストの表示
        region_list = ft.Column(spacing=5)
        for center_id, center_info in centers.items():
            region_name = center_info.get("name", "不明")
            region_list.controls.append(
                ft.ListTile(
                    title=ft.Text(region_name),
                    subtitle=ft.Text(f"ID: {center_id}"),
                    on_click=lambda e, center_id=center_id: show_region_details(center_id)
                )
            )

        # 初期表示用のセクション
        details_section = ft.Column()

        # 全体レイアウト
        page.add(
            ft.Row(
                [
                    ft.Container(
                        content=ft.Column(
                            [ft.Text("地域一覧", size=20, weight="bold"), region_list],
                            spacing=10,
                        ),
                        width=300,
                        bgcolor=ft.colors.LIGHT_BLUE_50,
                        padding=10,
                        border_radius=10,
                    ),
                    ft.Container(
                        content=details_section,
                        expand=True,
                        bgcolor=ft.colors.WHITE,
                        padding=10,
                        border_radius=10,
                    ),
                ],
                spacing=20,
            )
        )
    except requests.RequestException as e:
        page.add(ft.Text(f"エラー: {e}", color=ft.colors.RED, size=20))

ft.app(target=main)
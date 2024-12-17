import flet as ft
import requests
import sqlite3

# API URL
URL = "http://www.jma.go.jp/bosai/common/const/area.json"
DB_FILE = "weather_forecast.db"

# SQLiteデータベースの初期化
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # テーブル作成
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS regions (
            id TEXT PRIMARY KEY,
            name TEXT,
            en_name TEXT,
            office_name TEXT,
            children TEXT
        )
    ''')
    conn.commit()
    conn.close()

# 地域情報をデータベースに保存
def save_region_to_db(region_id, name, en_name, office_name, children):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # 挿入または更新
    cursor.execute('''
        INSERT INTO regions (id, name, en_name, office_name, children)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            name=excluded.name,
            en_name=excluded.en_name,
            office_name=excluded.office_name,
            children=excluded.children
    ''', (region_id, name, en_name, office_name, children))
    conn.commit()
    conn.close()

# 地域情報をデータベースから取得
def get_regions_from_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM regions")
    regions = cursor.fetchall()
    conn.close()
    return regions

def main(page: ft.Page):
    page.title = "天気予報"
    page.scroll = "auto"  # スクロール対応

    # 初期化
    init_db()

    # タイトル表示
    page.add(ft.Text("天気予報", size=30, weight="bold", color=ft.colors.BLUE_900))
    page.add(ft.Text("天気予報の地域情報", size=20))

    try:
        # JSONデータの取得
        response = requests.get(URL)
        response.raise_for_status()  # HTTPエラーをチェック
        data_json = response.json()

        # 地域データを取得しデータベースに保存
        centers = data_json.get("centers", {})
        for center_id, center_info in centers.items():
            name = center_info.get("name", "不明")
            en_name = center_info.get("enName", "不明")
            office_name = center_info.get("officeName", "不明")
            children = ",".join(center_info.get("children", []))
            save_region_to_db(center_id, name, en_name, office_name, children)

        # 表示を初期化
        def show_region_details(center_id):
            # 選択された地域の詳細を表示
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM regions WHERE id = ?", (center_id,))
            region_info = cursor.fetchone()
            conn.close()

            if region_info:
                details_section.controls = [
                    ft.Text(f"地域 ID: {region_info[0]}", weight="bold", size=18),
                    ft.Text(f"地域名 (JP): {region_info[1]}"),
                    ft.Text(f"地域名 (EN): {region_info[2]}"),
                    ft.Text(f"気象台: {region_info[3]}"),
                    ft.Text(f"子地域 IDs: {region_info[4]}"),
                ]
            else:
                details_section.controls = [ft.Text("地域情報が見つかりません")]
            page.update()

        # 地域リストの表示
        region_list = ft.Column(spacing=5)
        regions = get_regions_from_db()
        for region in regions:
            region_list.controls.append(
                ft.ListTile(
                    title=ft.Text(region[1]),  # 日本語名
                    subtitle=ft.Text(f"ID: {region[0]}"),
                    on_click=lambda e, center_id=region[0]: show_region_details(center_id)
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
